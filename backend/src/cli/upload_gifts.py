"""CLI tool to upload gift ideas from CSV to vector store."""

import argparse
import asyncio
import csv
import sys
from pathlib import Path
from uuid import uuid4

import structlog

from src.adapters.embeddings.openai_adapter import OpenAIEmbeddingAdapter
from src.adapters.vectors.s3_vectors_adapter import S3VectorsAdapter
from src.config.logging import configure_logging
from src.config.settings import get_settings
from src.domain.entities.gift import Gift
from src.domain.entities.price_range import PriceRange

logger = structlog.get_logger()

# CSV column names
REQUIRED_COLUMNS = ["name", "brief_description", "full_description", "price_range", "categories"]
OPTIONAL_COLUMNS = ["occasions", "recipient_types", "purchase_url", "has_affiliate_commission", "popularity_score"]


async def setup_index() -> None:
    """Create the S3 Vectors bucket and index if they don't exist."""
    settings = get_settings()
    configure_logging(settings.log_level)

    log = logger.bind(bucket=settings.s3_vectors_bucket, index=settings.s3_vectors_index)
    log.info("checking_index")

    vector_store = S3VectorsAdapter(
        bucket=settings.s3_vectors_bucket,
        index_name=settings.s3_vectors_index,
        region=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )

    created = await vector_store.ensure_index_exists(
        dimensions=settings.embedding_dimensions
    )

    if created:
        print(f"Created S3 Vectors index: {settings.s3_vectors_bucket}/{settings.s3_vectors_index}")
    else:
        print(f"Index already exists: {settings.s3_vectors_bucket}/{settings.s3_vectors_index}")


def parse_list(value: str) -> list[str]:
    """Parse a comma-separated string into a list."""
    if not value or value.strip() == "":
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_bool(value: str) -> bool:
    """Parse a string into a boolean."""
    return value.lower() in ("true", "yes", "1", "y")


def parse_float(value: str, default: float = 0.5) -> float:
    """Parse a string into a float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


async def upload_gifts(
    csv_path: Path,
    dry_run: bool = False,
) -> tuple[int, int, int]:
    """Upload gifts from CSV to vector store.

    Args:
        csv_path: Path to CSV file
        dry_run: If True, validate but don't upload

    Returns:
        Tuple of (created_count, updated_count, error_count)
    """
    settings = get_settings()
    configure_logging(settings.log_level)

    log = logger.bind(csv_path=str(csv_path), dry_run=dry_run)
    log.info("starting_upload")

    # Initialize adapters
    embedding_adapter = OpenAIEmbeddingAdapter(api_key=settings.openai_api_key)
    vector_store = S3VectorsAdapter(
        bucket=settings.s3_vectors_bucket,
        index_name=settings.s3_vectors_index,
        region=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )

    created_count = 0
    updated_count = 0
    error_count = 0

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        # Validate columns
        if reader.fieldnames is None:
            log.error("empty_csv")
            return 0, 0, 1

        missing_columns = set(REQUIRED_COLUMNS) - set(reader.fieldnames)
        if missing_columns:
            log.error("missing_required_columns", missing=list(missing_columns))
            print(f"Error: Missing required columns: {missing_columns}")
            print(f"Required columns: {REQUIRED_COLUMNS}")
            return 0, 0, 1

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                name = row["name"].strip()
                if not name:
                    log.warning("skipping_empty_name", row=row_num)
                    continue

                log.debug("processing_row", row=row_num, name=name)

                # Check if gift already exists
                existing_gift = await vector_store.find_by_name(name)

                # Parse row data
                brief_description = row["brief_description"].strip()
                full_description = row["full_description"].strip()
                price_range = PriceRange(row["price_range"].strip().lower())
                categories = parse_list(row["categories"])

                if not categories:
                    log.warning("skipping_no_categories", row=row_num, name=name)
                    print(f"Warning: Row {row_num} '{name}' has no categories, skipping")
                    continue

                # Optional fields
                occasions = parse_list(row.get("occasions", ""))
                recipient_types = parse_list(row.get("recipient_types", ""))
                purchase_url = row.get("purchase_url", "").strip() or None
                has_affiliate = parse_bool(row.get("has_affiliate_commission", "false"))
                popularity = parse_float(row.get("popularity_score", "0.5"), 0.5)

                # Use existing ID if updating, otherwise generate new
                gift_id = existing_gift.id if existing_gift else uuid4()

                # Generate embedding from gift content (include all searchable fields)
                embedding_parts = [
                    name,
                    brief_description,
                    f"Categories: {', '.join(categories)}",
                ]
                if occasions:
                    embedding_parts.append(f"Occasions: {', '.join(occasions)}")
                if recipient_types:
                    embedding_parts.append(f"Good for: {', '.join(recipient_types)}")
                embedding_text = ". ".join(embedding_parts)
                embedding = await embedding_adapter.embed_text(embedding_text)

                # Create gift entity
                gift = Gift(
                    id=gift_id,
                    name=name,
                    brief_description=brief_description,
                    full_description=full_description,
                    price_range=price_range,
                    categories=categories,
                    occasions=occasions,
                    recipient_types=recipient_types,
                    embedding=embedding,
                    popularity_score=popularity,
                    purchase_url=purchase_url,
                    has_affiliate_commission=has_affiliate,
                )

                if dry_run:
                    action = "update" if existing_gift else "create"
                    print(f"[DRY RUN] Would {action}: {name}")
                else:
                    await vector_store.upsert(gift)

                if existing_gift:
                    updated_count += 1
                    log.info("updated_gift", name=name, gift_id=str(gift_id))
                    print(f"Updated: {name}")
                else:
                    created_count += 1
                    log.info("created_gift", name=name, gift_id=str(gift_id))
                    print(f"Created: {name}")

            except Exception as e:
                error_count += 1
                log.error("row_error", row=row_num, error=str(e))
                print(f"Error on row {row_num}: {e}")

    log.info(
        "upload_complete",
        created=created_count,
        updated=updated_count,
        errors=error_count,
    )

    return created_count, updated_count, error_count


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Upload gift ideas from CSV to vector store",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CSV Format:
  Required columns: name, brief_description, full_description, price_range, categories
  Optional columns: occasions, recipient_types, purchase_url, has_affiliate_commission, popularity_score

  - price_range: budget, moderate, premium, or luxury
  - categories, occasions, recipient_types: comma-separated values
  - has_affiliate_commission: true/false/yes/no/1/0
  - popularity_score: 0.0 to 1.0 (default: 0.5)

Example CSV:
  name,brief_description,full_description,price_range,categories,purchase_url,has_affiliate_commission
  "Leather Journal","Hand-crafted journal","A beautiful journal...",moderate,"stationery,handmade",https://example.com,true
""",
    )

    parser.add_argument(
        "csv_file",
        type=Path,
        help="Path to CSV file containing gift ideas",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate CSV and show what would be uploaded without actually uploading",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Create the S3 Vectors bucket and index if they don't exist",
    )

    args = parser.parse_args()

    if not args.csv_file.exists():
        print(f"Error: File not found: {args.csv_file}")
        sys.exit(1)

    # Run setup if requested
    if args.setup:
        asyncio.run(setup_index())

    created, updated, errors = asyncio.run(
        upload_gifts(csv_path=args.csv_file, dry_run=args.dry_run)
    )

    print()
    print(f"Summary: {created} created, {updated} updated, {errors} errors")

    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

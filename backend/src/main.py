"""Main entry point for the Gift Recommendation MCP Server."""

import structlog

from src.adapters.embeddings.openai_adapter import OpenAIEmbeddingAdapter
from src.adapters.mcp import server as mcp_module
from src.adapters.mcp.server import create_mcp_server
from src.adapters.vectors.s3_vectors_adapter import S3VectorsAdapter
from src.config.logging import configure_logging
from src.config.settings import get_settings
from src.domain.services.recommendation_service import RecommendationService

logger = structlog.get_logger()


def main() -> None:
    """Initialize and run the MCP server."""
    # Load settings
    settings = get_settings()

    # Configure logging
    configure_logging(settings.log_level)

    log = logger.bind(server=settings.mcp_server_name)
    log.info("starting_server")

    # Create adapters
    embedding_adapter = OpenAIEmbeddingAdapter(api_key=settings.openai_api_key)
    vector_adapter = S3VectorsAdapter(
        bucket=settings.s3_vectors_bucket,
        index_name=settings.s3_vectors_index,
        region=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )

    # Create domain services
    recommendation_service = RecommendationService(
        embedding_provider=embedding_adapter,
        vector_store=vector_adapter,
    )

    # Create MCP server with service
    mcp = create_mcp_server(
        settings=settings,
        recommendation_service=recommendation_service,
        vector_store=vector_adapter,
    )
    mcp_module.mcp_server = mcp

    log.info("server_configured", adapters=["openai_embedding", "s3_vectors"])

    # Check transport mode from settings
    if settings.mcp_transport == "stdio":
        log.info("starting_stdio_server")
        mcp.run()
    else:
        log.info("starting_sse_server", host=settings.mcp_host, port=settings.mcp_port)
        mcp.run(transport="sse", host=settings.mcp_host, port=settings.mcp_port)


if __name__ == "__main__":
    main()

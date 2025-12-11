"""Main entry point for the Gift Recommendation MCP Server."""

import structlog

from src.adapters.embeddings.openai_adapter import OpenAIEmbeddingAdapter
from src.adapters.mcp import server as mcp_module
from src.adapters.mcp.server import create_mcp_server
from src.adapters.vectors.s3_vectors_adapter import S3VectorsAdapter
from src.config.logging import configure_logging
from src.config.settings import get_settings

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
    )

    # Create MCP server
    mcp = create_mcp_server(settings)
    mcp_module.mcp_server = mcp

    # Store adapters in server context for tool handlers
    mcp.state["embedding_adapter"] = embedding_adapter
    mcp.state["vector_adapter"] = vector_adapter
    mcp.state["settings"] = settings

    log.info("server_configured", adapters=["openai_embedding", "s3_vectors"])

    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()

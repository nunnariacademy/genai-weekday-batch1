"""Shared settings. Override any of them with environment variables."""
import os

CONTAINER_NAME = os.getenv("PG_CONTAINER", "mcp-demo-postgres")
DB_CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": int(os.getenv("PG_PORT", "5433")),  # 5433 so it won't clash with a local Postgres
    "dbname": os.getenv("PG_DB", "company"),
    "user": os.getenv("PG_USER", "demo"),
    "password": os.getenv("PG_PASSWORD", "demo123"),
}

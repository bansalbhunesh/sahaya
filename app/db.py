"""Shared MongoDB client for dashboard reads and seeding.

Agent writes never use this module — they go through the MongoDB MCP server.
"""

import logging
import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

log = logging.getLogger("sahaya.db")

DB_NAME = os.environ.get("SAHAYA_DB", "sahaya")

_client: MongoClient | None = None


def connection_string() -> str:
    uri = os.environ.get("MDB_MCP_CONNECTION_STRING", "")
    if not uri:
        raise RuntimeError(
            "MDB_MCP_CONNECTION_STRING is not set. Copy .env.example to .env "
            "and fill in your Atlas connection string."
        )
    return uri


def client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(connection_string(), serverSelectionTimeoutMS=8000)
        log.info('{"event":"mongo_client_created","db":"%s"}', DB_NAME)
    return _client


def db():
    return client()[DB_NAME]

"""
Common database types and utilities shared across models.

This module provides reusable database type definitions to avoid duplication
across model files.
"""
import uuid
import json
from sqlalchemy import CHAR, Text
from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB


class UUID(TypeDecorator):
    """
    Platform-independent UUID type.

    Uses PostgreSQL's native UUID type when available, or CHAR(36) for SQLite
    and other databases. Handles conversion automatically.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Load the appropriate UUID implementation for the database dialect."""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        """Convert Python UUID to database format."""
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        """Convert database format to Python UUID."""
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


class JSONType(TypeDecorator):
    """
    Platform-independent JSON type.

    Uses PostgreSQL's native JSONB type when available, or Text with JSON
    serialization for SQLite and other databases.
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Load the appropriate JSON implementation for the database dialect."""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        """Convert Python dict to database format."""
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        """Convert database format to Python dict."""
        if value is None:
            return value
        if isinstance(value, dict):
            return value
        return json.loads(value)

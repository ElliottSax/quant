"""Field selection utilities for API responses.

Allows clients to specify which fields they want returned,
reducing bandwidth and improving performance.

Usage:
    # In endpoint:
    @router.get("/items")
    async def list_items(fields: str = Query(None)):
        items = await get_items()
        return select_fields(items, fields)

    # Client request:
    GET /api/v1/items?fields=id,name,price

"""

from typing import Any, TypeVar
from pydantic import BaseModel

from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def parse_field_selector(fields: str | None) -> set[str] | None:
    """
    Parse field selector string into set of field names.

    Args:
        fields: Comma-separated field names or None

    Returns:
        Set of field names or None if no selection
    """
    if not fields:
        return None

    # Parse comma-separated fields
    field_set = set()
    for field in fields.split(","):
        field = field.strip()
        if field:
            field_set.add(field)

    return field_set if field_set else None


def select_fields(data: Any, fields: str | None) -> Any:
    """
    Select specific fields from response data.

    Args:
        data: Response data (dict, list, or Pydantic model)
        fields: Comma-separated field names or None

    Returns:
        Filtered data with only selected fields
    """
    field_set = parse_field_selector(fields)

    if not field_set:
        return data

    return _filter_fields(data, field_set)


def _filter_fields(data: Any, fields: set[str]) -> Any:
    """
    Recursively filter fields from data.

    Args:
        data: Data to filter
        fields: Set of field names to include

    Returns:
        Filtered data
    """
    if data is None:
        return None

    # Handle Pydantic models
    if isinstance(data, BaseModel):
        data = data.model_dump()

    # Handle dictionaries
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if k in fields}

    # Handle lists
    if isinstance(data, list):
        return [_filter_fields(item, fields) for item in data]

    # Return other types unchanged
    return data


def select_nested_fields(data: Any, fields: str | None) -> Any:
    """
    Select fields with nested field support.

    Supports dot notation for nested fields:
        fields=id,name,politician.name,politician.party

    Args:
        data: Response data
        fields: Comma-separated field names with dot notation

    Returns:
        Filtered data with nested field support
    """
    field_selector = parse_field_selector(fields)

    if not field_selector:
        return data

    # Parse nested fields
    nested_fields = {}
    top_level_fields = set()

    for field in field_selector:
        if "." in field:
            parts = field.split(".", 1)
            parent = parts[0]
            child = parts[1]
            if parent not in nested_fields:
                nested_fields[parent] = set()
            nested_fields[parent].add(child)
        else:
            top_level_fields.add(field)

    return _filter_nested_fields(data, top_level_fields, nested_fields)


def _filter_nested_fields(
    data: Any,
    top_level: set[str],
    nested: dict[str, set[str]],
) -> Any:
    """
    Recursively filter nested fields.

    Args:
        data: Data to filter
        top_level: Top-level field names
        nested: Dict of parent -> child field names

    Returns:
        Filtered data
    """
    if data is None:
        return None

    # Handle Pydantic models
    if isinstance(data, BaseModel):
        data = data.model_dump()

    # Handle dictionaries
    if isinstance(data, dict):
        result = {}

        # Include top-level fields
        for field in top_level:
            if field in data:
                result[field] = data[field]

        # Include nested fields
        for parent, children in nested.items():
            if parent in data:
                child_data = data[parent]
                if isinstance(child_data, dict):
                    result[parent] = {k: v for k, v in child_data.items() if k in children}
                elif isinstance(child_data, list):
                    result[parent] = [
                        {k: v for k, v in item.items() if k in children}
                        if isinstance(item, dict) else item
                        for item in child_data
                    ]
                else:
                    result[parent] = child_data

        return result

    # Handle lists
    if isinstance(data, list):
        return [_filter_nested_fields(item, top_level, nested) for item in data]

    return data


class FieldSelector:
    """
    Field selector for use as FastAPI dependency.

    Usage:
        @router.get("/items")
        async def list_items(
            selector: FieldSelector = Depends(FieldSelector.from_query),
        ):
            items = await get_items()
            return selector.apply(items)
    """

    def __init__(self, fields: str | None = None, nested: bool = False):
        """
        Initialize field selector.

        Args:
            fields: Comma-separated field names
            nested: Whether to support nested fields (dot notation)
        """
        self.fields = fields
        self.nested = nested
        self._field_set = parse_field_selector(fields)

    @classmethod
    def from_query(cls, fields: str | None = None) -> "FieldSelector":
        """Create FieldSelector from query parameter."""
        return cls(fields=fields, nested=True)

    def apply(self, data: Any) -> Any:
        """
        Apply field selection to data.

        Args:
            data: Data to filter

        Returns:
            Filtered data
        """
        if self.nested:
            return select_nested_fields(data, self.fields)
        return select_fields(data, self.fields)

    @property
    def has_selection(self) -> bool:
        """Check if field selection is active."""
        return self._field_set is not None and len(self._field_set) > 0

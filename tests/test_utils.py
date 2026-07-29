import pytest
from utils import generate_uuid, get_timestamp


def test_generate_uuid():
    """Test that generate_uuid returns a valid UUID v4."""
    uuid_str = generate_uuid()
    
    # Check it's a string
    assert isinstance(uuid_str, str)
    
    # Check UUID format (8-4-4-4-12 hex digits)
    import re
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    assert re.match(uuid_pattern, uuid_str, re.IGNORECASE)
    
    # Check uniqueness
    uuid2 = generate_uuid()
    assert uuid_str != uuid2


def test_get_timestamp():
    """Test that get_timestamp returns valid ISO-8601 timestamp."""
    timestamp = get_timestamp()
    
    # Check it's a string
    assert isinstance(timestamp, str)
    
    # Check ISO-8601 format with Z suffix
    import re
    iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$'
    assert re.match(iso_pattern, timestamp)
    
    # Check it can be parsed
    from datetime import datetime
    parsed = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    assert parsed is not None

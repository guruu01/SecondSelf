import uuid
from datetime import datetime
from typing import Optional


def generate_uuid() -> str:
    """
    Generate a unique UUID v4.
    
    Returns:
        str: UUID v4 string
    """
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """
    Get current timestamp in ISO-8601 format.
    
    Returns:
        str: ISO-8601 formatted timestamp
    """
    return datetime.utcnow().isoformat() + "Z"

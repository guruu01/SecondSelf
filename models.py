from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import json


@dataclass
class RawCapture:
    """
    Data model for raw captures before processing.
    
    Attributes:
        id: Unique UUID v4 identifier
        timestamp: ISO-8601 formatted timestamp
        type: One of "note", "link", or "file"
        content: The actual content being captured
        source: Optional source identifier
        metadata: Additional metadata (url, filename, etc.)
    """
    id: str
    timestamp: str
    type: str
    content: str
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate capture type and initialize metadata if None."""
        valid_types = ["note", "link", "file"]
        if self.type not in valid_types:
            raise ValueError(f"Invalid type: {self.type}. Must be one of {valid_types}")
        
        if self.metadata is None:
            self.metadata = {}
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'RawCapture':
        """Create RawCapture from JSON string."""
        data = json.loads(json_str)
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

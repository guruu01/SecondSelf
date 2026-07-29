from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
import json
import numpy as np


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


@dataclass
class WikiNote:
    """
    Data model for processed wiki notes with classification and linking.
    
    Attributes:
        id: Unique UUID v4 identifier for this wiki note
        timestamp: ISO-8601 formatted timestamp when wiki note was created
        raw_id: UUID of the original raw capture
        content: The content from the raw capture
        category: PARA category (Projects, Areas, Resources, Archives)
        tags: List of tags from classification
        summary: One-line summary from classification
        links: List of linked wiki note IDs with confidence scores
        embedding_path: Path to cached embedding file (if exists)
    """
    id: str
    timestamp: str
    raw_id: str
    content: str
    category: str
    tags: List[str] = field(default_factory=list)
    summary: str = ""
    links: Dict[str, float] = field(default_factory=dict)
    embedding_path: Optional[str] = None
    
    def __post_init__(self):
        """Validate PARA category and initialize defaults."""
        valid_categories = ["Projects", "Areas", "Resources", "Archives"]
        if self.category not in valid_categories:
            raise ValueError(f"Invalid category: {self.category}. Must be one of {valid_categories}")
        
        if not self.tags:
            self.tags = []
        
        if not self.links:
            self.links = {}
    
    def to_json(self) -> str:
        """Convert to JSON string (embedding excluded)."""
        data = asdict(self)
        # Convert numpy arrays if present
        if 'embedding' in data and data['embedding'] is not None:
            if isinstance(data['embedding'], np.ndarray):
                data['embedding'] = data['embedding'].tolist()
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WikiNote':
        """Create WikiNote from JSON string."""
        data = json.loads(json_str)
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class GraphNode:
    """
    Data model for graph nodes representing wiki notes.
    
    Attributes:
        id: Unique UUID v4 identifier (wiki note ID)
        label: Display label for the node
        title: Full title/summary of the note
        category: PARA category (Projects, Areas, Resources, Archives)
        tags: List of tags from classification
        size: Node size based on link count (centrality)
        color: Color based on PARA category
        content: Full content of the note
        link_count: Number of links to/from this node
    """
    id: str
    label: str
    title: str
    category: str
    tags: List[str] = field(default_factory=list)
    size: int = 20
    color: str = "#97C2FC"
    content: str = ""
    link_count: int = 0
    
    def __post_init__(self):
        """Validate PARA category."""
        valid_categories = ["Projects", "Areas", "Resources", "Archives"]
        if self.category not in valid_categories:
            raise ValueError(f"Invalid category: {self.category}. Must be one of {valid_categories}")
        
        if not self.tags:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class GraphEdge:
    """
    Data model for graph edges representing links between wiki notes.
    
    Attributes:
        from_: Source node ID (wiki note ID)
        to: Target node ID (wiki note ID)
        weight: Similarity score (0-1)
        title: Hover title for the edge
    """
    from_: str
    to: str
    weight: float
    title: str = ""
    
    def __post_init__(self):
        """Validate weight range."""
        # Clamp weight to [0, 1] to handle floating point precision issues
        self.weight = max(0.0, min(1.0, self.weight))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "from": self.from_,
            "to": self.to,
            "weight": self.weight,
            "title": self.title
        }


@dataclass
class GraphData:
    """
    Data model for complete graph structure.
    
    Attributes:
        nodes: List of graph nodes
        edges: List of graph edges
    """
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges]
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

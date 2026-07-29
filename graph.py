"""
Graph building module for converting wiki notes to interactive knowledge graph.
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from models import WikiNote, GraphNode, GraphEdge, GraphData


# PARA category color scheme
CATEGORY_COLORS = {
    "Projects": "#FF6B6B",    # Red
    "Areas": "#4ECDC4",       # Teal
    "Resources": "#45B7D1",   # Blue
    "Archives": "#96CEB4"     # Green
}


def load_wiki_notes() -> Dict[str, WikiNote]:
    """
    Load all wiki notes from the wiki directory.
    
    Returns:
        Dict mapping wiki note IDs to WikiNote objects.
    """
    wiki_dir = Path("wiki")
    wiki_notes = {}
    
    for json_file in wiki_dir.glob("*.json"):
        if json_file.name == "index.json":
            continue
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            wiki_note = WikiNote.from_json(json.dumps(data))
            wiki_notes[wiki_note.id] = wiki_note
    
    return wiki_notes


def calculate_node_size(link_count: int, min_size: int = 15, max_size: int = 50) -> int:
    """
    Calculate node size based on link count (centrality).
    
    Args:
        link_count: Number of links to/from this node
        min_size: Minimum node size
        max_size: Maximum node size
    
    Returns:
        Calculated node size.
    """
    # Logarithmic scaling for better visual distribution
    if link_count == 0:
        return min_size
    size = min_size + min(max_size - min_size, int(10 * (link_count ** 0.5)))
    return size


def build_nodes(wiki_notes: Dict[str, WikiNote]) -> List[GraphNode]:
    """
    Convert wiki notes to graph nodes.
    
    Args:
        wiki_notes: Dict mapping wiki note IDs to WikiNote objects.
    
    Returns:
        List of GraphNode objects.
    """
    nodes = []
    
    # Calculate link counts for each note
    link_counts = {}
    for wiki_id, note in wiki_notes.items():
        # Count outgoing links
        link_counts[wiki_id] = len(note.links)
    
    # Count incoming links
    for wiki_id, note in wiki_notes.items():
        for linked_id in note.links.keys():
            if linked_id in link_counts:
                link_counts[linked_id] += 1
    
    for wiki_id, note in wiki_notes.items():
        # Generate label from summary (truncate if too long)
        label = note.summary[:50] + "..." if len(note.summary) > 50 else note.summary
        if not label:
            label = note.content[:30] + "..." if len(note.content) > 30 else note.content
        
        # Calculate node size based on total link count
        total_links = link_counts.get(wiki_id, 0)
        size = calculate_node_size(total_links)
        
        # Assign color based on category
        color = CATEGORY_COLORS.get(note.category, "#97C2FC")
        
        node = GraphNode(
            id=wiki_id,
            label=label,
            title=note.summary or "No summary",
            category=note.category,
            tags=note.tags,
            size=size,
            color=color,
            content=note.content,
            link_count=total_links
        )
        nodes.append(node)
    
    return nodes


def build_edges(wiki_notes: Dict[str, WikiNote]) -> List[GraphEdge]:
    """
    Convert wiki links to graph edges.
    
    Args:
        wiki_notes: Dict mapping wiki note IDs to WikiNote objects.
    
    Returns:
        List of GraphEdge objects.
    """
    edges = []
    seen_edges = set()  # To avoid duplicate edges
    
    for wiki_id, note in wiki_notes.items():
        for linked_id, similarity in note.links.items():
            # Create edge key for deduplication (sorted to handle bidirectional)
            edge_key = tuple(sorted([wiki_id, linked_id]))
            
            if edge_key in seen_edges:
                continue
            
            seen_edges.add(edge_key)
            
            # Create edge title with similarity score
            title = f"Similarity: {similarity:.2f}"
            
            edge = GraphEdge(
                from_=wiki_id,
                to=linked_id,
                weight=similarity,
                title=title
            )
            edges.append(edge)
    
    return edges


def build_graph() -> GraphData:
    """
    Build complete graph from wiki notes.
    
    Returns:
        GraphData object with nodes and edges.
    """
    wiki_notes = load_wiki_notes()
    nodes = build_nodes(wiki_notes)
    edges = build_edges(wiki_notes)
    
    return GraphData(nodes=nodes, edges=edges)


def export_graph(output_path: str = "graph.json") -> None:
    """
    Export graph data to JSON file.
    
    Args:
        output_path: Path to output JSON file.
    """
    graph_data = build_graph()
    
    output_file = Path(output_path)
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(graph_data.to_json())
    
    print(f"Graph exported to {output_path}")
    print(f"Nodes: {len(graph_data.nodes)}, Edges: {len(graph_data.edges)}")


if __name__ == "__main__":
    export_graph()

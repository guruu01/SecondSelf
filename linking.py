"""
Auto-linking module for finding and linking related wiki notes based on semantic similarity.
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from embeddings import compute_embedding, compute_similarity, load_embedding, save_embedding
from models import WikiNote


def load_wiki_note(wiki_id: str) -> WikiNote:
    """
    Load a wiki note from the wiki directory.
    
    Args:
        wiki_id: UUID of the wiki note.
    
    Returns:
        WikiNote object.
    """
    wiki_path = Path(f"wiki/{wiki_id}.json")
    if not wiki_path.exists():
        raise FileNotFoundError(f"Wiki note not found: {wiki_path}")
    
    with open(wiki_path, 'r', encoding='utf-8') as f:
        wiki_data = json.load(f)
    
    return WikiNote.from_json(json.dumps(wiki_data))


def get_all_wiki_notes() -> Dict[str, WikiNote]:
    """
    Load all wiki notes from the wiki directory.
    
    Returns:
        Dict mapping wiki_id to WikiNote objects.
    """
    wiki_dir = Path("wiki")
    notes = {}
    
    for file_path in wiki_dir.glob("*.json"):
        if file_path.name == "index.json":
            continue
        
        wiki_id = file_path.stem
        try:
            note = load_wiki_note(wiki_id)
            notes[wiki_id] = note
        except Exception as e:
            print(f"Error loading {wiki_id}: {e}")
    
    return notes


def get_or_compute_embedding(wiki_id: str, wiki_note: WikiNote) -> np.ndarray:
    """
    Get cached embedding or compute new one for a wiki note.
    
    Args:
        wiki_id: UUID of the wiki note.
        wiki_note: WikiNote object.
    
    Returns:
        Embedding array.
    """
    embedding_path = Path(f"wiki/embeddings/{wiki_id}.npy")
    
    # Check cache first
    if embedding_path.exists():
        return load_embedding(str(embedding_path))
    
    # Compute new embedding
    text_to_embed = f"{wiki_note.summary} {wiki_note.content}"
    embedding = compute_embedding(text_to_embed)
    
    # Save to cache
    save_embedding(embedding, str(embedding_path))
    
    # Update wiki note with embedding path
    wiki_note.embedding_path = str(embedding_path)
    wiki_path = Path(f"wiki/{wiki_id}.json")
    with open(wiki_path, 'w', encoding='utf-8') as f:
        f.write(wiki_note.to_json())
    
    return embedding


def find_related_notes(
    wiki_id: str,
    threshold: float = 0.75,
    max_results: int = 10
) -> List[Tuple[str, float]]:
    """
    Find related wiki notes based on semantic similarity.
    
    Args:
        wiki_id: UUID of the wiki note to find relations for.
        threshold: Minimum similarity score to consider as related.
        max_results: Maximum number of related notes to return.
    
    Returns:
        List of tuples (wiki_id, similarity_score) sorted by similarity.
    """
    # Load all wiki notes
    all_notes = get_all_wiki_notes()
    
    if wiki_id not in all_notes:
        raise ValueError(f"Wiki note {wiki_id} not found")
    
    if len(all_notes) == 1:
        return []
    
    # Get embedding for the query note
    query_note = all_notes[wiki_id]
    query_embedding = get_or_compute_embedding(wiki_id, query_note)
    
    # Compute similarities with all other notes
    similarities = []
    for other_id, other_note in all_notes.items():
        if other_id == wiki_id:
            continue
        
        other_embedding = get_or_compute_embedding(other_id, other_note)
        similarity = compute_similarity(query_embedding, other_embedding)
        
        if similarity >= threshold:
            similarities.append((other_id, similarity))
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Return top results
    return similarities[:max_results]


def auto_link(wiki_id: str, threshold: float = 0.75) -> List[str]:
    """
    Automatically link a wiki note to related notes.
    
    Args:
        wiki_id: UUID of the wiki note to link.
        threshold: Minimum similarity score for linking.
    
    Returns:
        List of linked wiki note IDs.
    """
    # Find related notes
    related = find_related_notes(wiki_id, threshold)
    
    if not related:
        return []
    
    # Load the wiki note
    wiki_note = load_wiki_note(wiki_id)
    
    # Add links to the wiki note
    for related_id, similarity in related:
        wiki_note.links[related_id] = similarity
    
    # Save updated wiki note
    wiki_path = Path(f"wiki/{wiki_id}.json")
    with open(wiki_path, 'w', encoding='utf-8') as f:
        f.write(wiki_note.to_json())
    
    # Add reciprocal links
    for related_id, similarity in related:
        related_note = load_wiki_note(related_id)
        related_note.links[wiki_id] = similarity
        related_path = Path(f"wiki/{related_id}.json")
        with open(related_path, 'w', encoding='utf-8') as f:
            f.write(related_note.to_json())
    
    # Update wiki index
    index_path = Path("wiki/index.json")
    with open(index_path, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    index["notes"][wiki_id]["link_count"] = len(wiki_note.links)
    for related_id, _ in related:
        index["notes"][related_id]["link_count"] = index["notes"][related_id].get("link_count", 0) + 1
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    return [r[0] for r in related]


def batch_link(wiki_ids: List[str], threshold: float = 0.75) -> Dict[str, List[str]]:
    """
    Process multiple wiki notes for linking.
    
    Args:
        wiki_ids: List of wiki note IDs to process.
        threshold: Minimum similarity score for linking.
    
    Returns:
        Dict mapping wiki_id to list of linked note IDs.
    """
    results = {}
    
    for i, wiki_id in enumerate(wiki_ids):
        print(f"Linking {i+1}/{len(wiki_ids)}: {wiki_id}")
        
        try:
            linked = auto_link(wiki_id, threshold)
            results[wiki_id] = linked
            print(f"  Linked to {len(linked)} notes")
        except Exception as e:
            print(f"  Error linking {wiki_id}: {e}")
            results[wiki_id] = []
    
    return results


if __name__ == "__main__":
    # Test auto-linking
    import sys
    
    if len(sys.argv) > 1:
        wiki_id = sys.argv[1]
        threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.75
        linked = auto_link(wiki_id, threshold)
        print(f"Linked to {len(linked)} notes: {linked}")
    else:
        print("Usage: python linking.py <wiki_id> [threshold]")

"""
Wiki creation module for transforming classified raw captures into wiki notes.
"""
import json
from pathlib import Path
from typing import Dict, Any
from models import WikiNote, RawCapture
from utils import generate_uuid, get_timestamp
from classify import classify_capture


def load_raw_capture(raw_id: str) -> RawCapture:
    """
    Load a raw capture from the raw directory.
    
    Args:
        raw_id: UUID of the raw capture.
    
    Returns:
        RawCapture object.
    """
    raw_path = Path(f"raw/{raw_id}.json")
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw capture not found: {raw_path}")
    
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    return RawCapture.from_json(json.dumps(raw_data))


def get_wiki_index() -> Dict[str, Any]:
    """
    Load the wiki index.
    
    Returns:
        Dict containing wiki index data.
    """
    index_path = Path("wiki/index.json")
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"notes": {}, "last_updated": None}


def save_wiki_index(index: Dict[str, Any]) -> None:
    """
    Save the wiki index.
    
    Args:
        index: Wiki index data to save.
    """
    index_path = Path("wiki/index.json")
    index_path.parent.mkdir(exist_ok=True)
    
    index["last_updated"] = get_timestamp()
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


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


def create_wiki_note(raw_id: str, classification: Dict[str, Any]) -> str:
    """
    Transform a classified raw capture into a wiki note.
    
    Args:
        raw_id: UUID of the raw capture.
        classification: Classification result from classify_capture().
    
    Returns:
        UUID of the created wiki note.
    """
    # Load raw capture
    raw_capture = load_raw_capture(raw_id)
    
    # Generate new UUID for wiki note
    wiki_id = generate_uuid()
    
    # Create wiki note
    wiki_note = WikiNote(
        id=wiki_id,
        timestamp=get_timestamp(),
        raw_id=raw_id,
        content=raw_capture.content,
        category=classification["category"],
        tags=classification["tags"],
        summary=classification["summary"],
        links={},
        embedding_path=None
    )
    
    # Save wiki note
    wiki_path = Path(f"wiki/{wiki_id}.json")
    wiki_path.parent.mkdir(exist_ok=True)
    
    with open(wiki_path, 'w', encoding='utf-8') as f:
        f.write(wiki_note.to_json())
    
    # Update wiki index
    index = get_wiki_index()
    index["notes"][wiki_id] = {
        "raw_id": raw_id,
        "category": wiki_note.category,
        "tags": wiki_note.tags,
        "summary": wiki_note.summary,
        "created_at": wiki_note.timestamp,
        "link_count": 0
    }
    save_wiki_index(index)
    
    return wiki_id


if __name__ == "__main__":
    # Test wiki creation
    import sys
    
    if len(sys.argv) > 1:
        raw_id = sys.argv[1]
        classification = classify_capture(raw_id)
        wiki_id = create_wiki_note(raw_id, classification)
        print(f"Created wiki note: {wiki_id}")
    else:
        print("Usage: python wiki.py <raw_id>")

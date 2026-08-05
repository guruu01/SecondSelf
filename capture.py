import json
import os
import shutil
from pathlib import Path
from typing import Optional
from utils import generate_uuid, get_timestamp
from models import RawCapture
from db import get_db, RawCaptureDB, raw_capture_to_db, db_to_raw_capture, init_db, is_db_available


# Initialize database on import (optional)
init_db()

# Constants
RAW_DIR = Path("raw")
INDEX_FILE = RAW_DIR / "index.json"


def _ensure_raw_dir():
    """Ensure raw directory exists (for file backup)."""
    RAW_DIR.mkdir(exist_ok=True)


def _load_index() -> dict:
    """Load the master index from raw/index.json (legacy support)."""
    if not INDEX_FILE.exists():
        return {"captures": []}
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save_index(index: dict):
    """Save the master index to raw/index.json (legacy support)."""
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def _update_index(capture_id: str, capture_type: str, timestamp: str):
    """Add a new capture to the master index (legacy support)."""
    index = _load_index()
    index["captures"].append({
        "id": capture_id,
        "type": capture_type,
        "timestamp": timestamp
    })
    _save_index(index)


def capture_note(content: str, source: Optional[str] = None) -> str:
    """
    Capture a text note into the raw directory.
    
    Args:
        content: The note content to capture
        source: Optional source identifier
    
    Returns:
        str: UUID of the saved capture
    
    Raises:
        ValueError: If content is empty or whitespace-only
    """
    # Validate content
    if not content or not content.strip():
        raise ValueError("Content cannot be empty")
    
    _ensure_raw_dir()
    
    # Generate ID and timestamp
    capture_id = generate_uuid()
    timestamp = get_timestamp()
    
    # Create RawCapture object
    capture = RawCapture(
        id=capture_id,
        timestamp=timestamp,
        type="note",
        content=content,
        source=source
    )
    
    # Save to database if available
    if is_db_available():
        try:
            db = next(get_db())
            db_capture = raw_capture_to_db(capture)
            db.add(db_capture)
            db.commit()
            db.close()
        except Exception as e:
            print(f"Warning: Failed to save to database: {e}")

    # Also save to file as backup
    _ensure_raw_dir()
    capture_file = RAW_DIR / f"{capture_id}.json"
    with open(capture_file, 'w', encoding='utf-8') as f:
        f.write(capture.to_json())

    # Also save as plain text file
    txt_file = RAW_DIR / f"{capture_id}.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(content)
    # Update index
    _update_index(capture_id, "note", timestamp)
    
    return capture_id


def capture_link(url: str) -> str:
    """
    Capture a URL into the raw directory.
    
    Args:
        url: The URL to capture
    
    Returns:
        str: UUID of the saved capture
    
    Raises:
        ValueError: If URL is invalid
    """
    # Basic URL validation
    if not url or not url.strip():
        raise ValueError("URL cannot be empty")
    
    # Simple validation - check for http/https prefix
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")
    
    _ensure_raw_dir()
    
    # Generate ID and timestamp
    capture_id = generate_uuid()
    timestamp = get_timestamp()
    
    # Create RawCapture object
    capture = RawCapture(
        id=capture_id,
        timestamp=timestamp,
        type="link",
        content=url,  # Store URL as content
        metadata={"url": url}
    )
    
    # Save to database if available
    if is_db_available():
        try:
            db = next(get_db())
            db_capture = raw_capture_to_db(capture)
            db.add(db_capture)
            db.commit()
            db.close()
        except Exception as e:
            print(f"Warning: Failed to save to database: {e}")

    # Also save to file as backup
    _ensure_raw_dir()
    capture_file = RAW_DIR / f"{capture_id}.json"
    with open(capture_file, 'w', encoding='utf-8') as f:
        f.write(capture.to_json())

    # Also save as a clickable .url shortcut file
    url_file = RAW_DIR / f"{capture_id}.url"
    with open(url_file, 'w', encoding='utf-8') as f:
        f.write(f"[InternetShortcut]\nURL={url}\n")
    
    # Update index
    _update_index(capture_id, "link", timestamp)
    
    return capture_id


def capture_file(file_path: str) -> str:
    """
    Capture a file into the raw directory.
    
    Args:
        file_path: Path to the file to capture
    
    Returns:
        str: UUID of the saved capture
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a text file
    """
    # Check file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Define file categories
    text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.csv'}
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    file_ext = Path(file_path).suffix.lower()

    if file_ext in text_extensions:
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            raise ValueError("File is not a valid text file (encoding error)")
    elif file_ext == '.pdf':
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        content = ""
        for page in reader.pages:
            content += page.extract_text() or ""
    elif file_ext in image_extensions:
        # No text extraction for images — just note it's an image
        content = f"[Image file: {Path(file_path).name}]"
    else:
        raise ValueError(f"Unsupported file type: {file_ext}. Only text, PDF, and image files are supported.")
    
    _ensure_raw_dir()
    
    # Generate ID and timestamp
    capture_id = generate_uuid()
    timestamp = get_timestamp()
    
    # Get original filename
    original_filename = Path(file_path).name
    
    # Create RawCapture object
    capture = RawCapture(
        id=capture_id,
        timestamp=timestamp,
        type="file",
        content=content,
        metadata={
            "original_filename": original_filename,
            "file_type": file_ext
        }
    )
    
    # Save to database if available
    if is_db_available():
        try:
            db = next(get_db())
            db_capture = raw_capture_to_db(capture)
            db.add(db_capture)
            db.commit()
            db.close()
        except Exception as e:
            print(f"Warning: Failed to save to database: {e}")

    # Also save to file as backup
    _ensure_raw_dir()
    # Copy the original file into raw/ with its original extension
    original_copy_path = RAW_DIR / f"{capture_id}{file_ext}"
    shutil.copy2(file_path, original_copy_path)

    # Save to file
    capture_file = RAW_DIR / f"{capture_id}.json"
    with open(capture_file, 'w', encoding='utf-8') as f:
        f.write(capture.to_json())
    
    # Update index
    _update_index(capture_id, "file", timestamp)
    
    return capture_id


def capture(content: str, type: str = "note", **kwargs) -> str:
    """
    Unified capture interface for any content type.
    
    Args:
        content: The content to capture
        type: One of "note", "link", or "file"
        **kwargs: Additional metadata (url, file_path, etc.)
    
    Returns:
        str: UUID of the saved capture
    
    Raises:
        ValueError: If type is invalid
    """
    if type == "note":
        return capture_note(content, source=kwargs.get('source'))
    elif type == "link":
        return capture_link(content)  # content is the URL
    elif type == "file":
        return capture_file(content)  # content is the file path
    else:
        raise ValueError(f"Invalid type: {type}. Must be one of 'note', 'link', 'file'")


if __name__ == "__main__":
    import sys
    
    # CLI interface
    if len(sys.argv) < 2:
        print("Usage: python capture.py <content> [--type note|link|file] [--source <source>]")
        sys.exit(1)
    
    content = sys.argv[1]
    capture_type = "note"
    source = None
    
    # Parse optional arguments
    for i in range(2, len(sys.argv)):
        if sys.argv[i] == "--type" and i + 1 < len(sys.argv):
            capture_type = sys.argv[i + 1]
        elif sys.argv[i] == "--source" and i + 1 < len(sys.argv):
            source = sys.argv[i + 1]
    
    try:
        capture_id = capture(content, type=capture_type, source=source)
        print(f"Captured successfully! ID: {capture_id}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

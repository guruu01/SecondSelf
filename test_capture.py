"""
Test script to validate capture pipeline with sample data.
This will create 10+ test captures to verify the system works.
"""

from capture import capture_note, capture_link, capture_file
import os


def test_note_captures():
    """Test capturing text notes."""
    print("Testing note captures...")
    
    notes = [
        "Remember to buy groceries on the way home",
        "Project idea: Build a personal knowledge graph system",
        "Meeting notes: Discuss Q4 roadmap with team",
        "Book recommendation: Atomic Habits by James Clear",
        "Recipe: Pasta carbonara with eggs and parmesan",
        "Quote: 'The only way to do great work is to love what you do'",
        "Idea: Use sentence-transformers for semantic similarity",
        "Todo: Fix the bug in the authentication module",
        "Thought: Maybe I should learn Rust next year",
        "Note: The coffee shop on 5th street has great wifi"
    ]
    
    note_ids = []
    for note in notes:
        try:
            note_id = capture_note(note)
            note_ids.append(note_id)
            print(f"  ✓ Captured note: {note[:30]}... -> {note_id}")
        except Exception as e:
            print(f"  ✗ Failed to capture note: {e}")
    
    print(f"Captured {len(note_ids)} notes successfully")
    return note_ids


def test_link_captures():
    """Test capturing URLs."""
    print("\nTesting link captures...")
    
    links = [
        "https://github.com",
        "https://www.python.org",
        "https://docs.streamlit.io",
        "https://huggingface.co"
    ]
    
    link_ids = []
    for link in links:
        try:
            link_id = capture_link(link)
            link_ids.append(link_id)
            print(f"  ✓ Captured link: {link} -> {link_id}")
        except Exception as e:
            print(f"  ✗ Failed to capture link: {e}")
    
    print(f"Captured {len(link_ids)} links successfully")
    return link_ids


def test_file_captures():
    """Test capturing files."""
    print("\nTesting file captures...")
    
    # Create a test file first
    test_file = "test_sample.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("This is a sample text file for testing the capture system.\nIt contains multiple lines.\n")
    
    file_ids = []
    try:
        file_id = capture_file(test_file)
        file_ids.append(file_id)
        print(f"  ✓ Captured file: {test_file} -> {file_id}")
    except Exception as e:
        print(f"  ✗ Failed to capture file: {e}")
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
    
    print(f"Captured {len(file_ids)} files successfully")
    return file_ids


def verify_index():
    """Verify the index was created correctly."""
    print("\nVerifying index...")
    
    import json
    from pathlib import Path
    
    index_file = Path("raw/index.json")
    if not index_file.exists():
        print("  ✗ Index file does not exist")
        return False
    
    with open(index_file, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    capture_count = len(index.get("captures", []))
    print(f"  ✓ Index contains {capture_count} captures")
    
    # Verify structure
    for capture in index["captures"]:
        if not all(key in capture for key in ["id", "type", "timestamp"]):
            print(f"  ✗ Invalid capture structure: {capture}")
            return False
    
    print("  ✓ Index structure is valid")
    return True


def verify_raw_files():
    """Verify raw files were created."""
    print("\nVerifying raw files...")
    
    from pathlib import Path
    import json
    
    raw_dir = Path("raw")
    json_files = list(raw_dir.glob("*.json"))
    # Exclude index.json
    json_files = [f for f in json_files if f.name != "index.json"]
    
    print(f"  ✓ Found {len(json_files)} capture files")
    
    # Verify file structure
    for file_path in json_files[:5]:  # Check first 5
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_fields = ["id", "timestamp", "type", "content"]
        if not all(field in data for field in required_fields):
            print(f"  ✗ Invalid file structure: {file_path.name}")
            return False
    
    print("  ✓ File structures are valid")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("SecondSelf - Capture Pipeline Test")
    print("=" * 60)
    
    note_ids = test_note_captures()
    link_ids = test_link_captures()
    file_ids = test_file_captures()
    
    total_captures = len(note_ids) + len(link_ids) + len(file_ids)
    print(f"\n{'=' * 60}")
    print(f"Total captures: {total_captures}")
    print(f"{'=' * 60}")
    
    if total_captures >= 10:
        print("✓ SUCCESS: Captured 10+ items")
    else:
        print(f"✗ FAILED: Only captured {total_captures} items (need 10+)")
    
    verify_index()
    verify_raw_files()
    
    print("\nTest complete!")

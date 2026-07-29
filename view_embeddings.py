import json
import numpy as np
from pathlib import Path
import os

# Paths
WIKI_DIR = Path("wiki")
EMBEDDINGS_DIR = WIKI_DIR / "embeddings"
INDEX_FILE = WIKI_DIR / "index.json"

def load_index():
    """Load the wiki index.json file"""
    with open(INDEX_FILE, 'r') as f:
        return json.load(f)

def load_embedding(note_id):
    """Load embedding for a specific note ID"""
    embedding_path = EMBEDDINGS_DIR / f"{note_id}.npy"
    if embedding_path.exists():
        return np.load(embedding_path)
    return None

def display_embeddings(limit=5):
    """Display embeddings with their note metadata"""
    index = load_index()
    notes = index.get('notes', {})
    
    print(f"Total notes in index: {len(notes)}")
    print(f"Embedding files found: {len(list(EMBEDDINGS_DIR.glob('*.npy')))}")
    print("\n" + "="*80)
    
    count = 0
    for note_id, note_data in notes.items():
        if count >= limit:
            break
            
        embedding = load_embedding(note_id)
        if embedding is not None:
            print(f"\nNote ID: {note_id}")
            print(f"Category: {note_data.get('category', 'N/A')}")
            print(f"Summary: {note_data.get('summary', 'N/A')}")
            print(f"Tags: {', '.join(note_data.get('tags', []))}")
            print(f"Embedding shape: {embedding.shape}")
            print(f"Embedding dtype: {embedding.dtype}")
            print(f"First 10 values: {embedding[:10]}")
            print(f"Min: {embedding.min():.4f}, Max: {embedding.max():.4f}, Mean: {embedding.mean():.4f}")
            print("-" * 80)
            count += 1
        else:
            print(f"\nNote ID: {note_id} - No embedding file found")
    
    if count < len(notes):
        print(f"\n... and {len(notes) - count} more notes")

def display_all_embeddings_summary():
    """Display summary of all embeddings"""
    index = load_index()
    notes = index.get('notes', {})
    
    print(f"\nSummary of all {len(notes)} embeddings:")
    print("="*80)
    
    categories = {}
    for note_id, note_data in notes.items():
        cat = note_data.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nBy category:")
    for cat, count in categories.items():
        print(f"  {cat}: {count}")
    
    # Load first embedding to show dimensions
    first_note_id = list(notes.keys())[0]
    first_embedding = load_embedding(first_note_id)
    if first_embedding is not None:
        print(f"\nEmbedding dimensions: {first_embedding.shape[0]}")
        print(f"Embedding type: {first_embedding.dtype}")

if __name__ == "__main__":
    print("Viewing Wiki Embeddings")
    print("="*80)
    
    # Show detailed view of first 5 embeddings
    display_embeddings(limit=5)
    
    # Show summary of all
    display_all_embeddings_summary()

"""
End-to-end pipeline for processing raw captures into linked wiki notes.

Chains classification → wiki creation → auto-linking.
"""
import sys
from pathlib import Path
from classify import classify_capture
from wiki import create_wiki_note
from linking import auto_link


def process_capture(raw_id: str, link_threshold: float = 0.75, skip_linking: bool = False) -> str:
    """
    Process a raw capture through the full pipeline.
    
    Args:
        raw_id: UUID of the raw capture to process.
        link_threshold: Similarity threshold for auto-linking.
        skip_linking: If True, skip the auto-linking step.
    
    Returns:
        UUID of the created wiki note.
    """
    print(f"Processing raw capture: {raw_id}")
    
    # Step 1: Classify
    print("  Step 1/3: Classifying...")
    classification = classify_capture(raw_id)
    print(f"    Category: {classification['category']}")
    print(f"    Tags: {', '.join(classification['tags'])}")
    print(f"    Summary: {classification['summary']}")
    
    # Step 2: Create wiki note
    print("  Step 2/3: Creating wiki note...")
    wiki_id = create_wiki_note(raw_id, classification)
    print(f"    Created wiki note: {wiki_id}")
    
    # Step 3: Auto-link (optional)
    if not skip_linking:
        print("  Step 3/3: Auto-linking...")
        try:
            linked = auto_link(wiki_id, link_threshold)
            print(f"    Linked to {len(linked)} notes")
        except Exception as e:
            print(f"    Linking skipped: {e}")
    else:
        print("  Step 3/3: Skipping auto-linking")
    
    print(f"Processing complete: {wiki_id}")
    return wiki_id


def batch_process(raw_ids: list, link_threshold: float = 0.75, skip_linking: bool = False) -> dict:
    """
    Process multiple raw captures through the pipeline.
    
    Args:
        raw_ids: List of raw capture UUIDs to process.
        link_threshold: Similarity threshold for auto-linking.
        skip_linking: If True, skip the auto-linking step.
    
    Returns:
        Dict mapping raw_id to wiki_id.
    """
    results = {}
    
    for i, raw_id in enumerate(raw_ids):
        print(f"\n{'='*60}")
        print(f"Batch processing {i+1}/{len(raw_ids)}")
        print(f"{'='*60}")
        
        try:
            wiki_id = process_capture(raw_id, link_threshold, skip_linking)
            results[raw_id] = wiki_id
        except Exception as e:
            print(f"ERROR: Failed to process {raw_id}: {e}")
            results[raw_id] = None
    
    print(f"\n{'='*60}")
    print(f"Batch processing complete")
    print(f"{'='*60}")
    print(f"Processed: {len([r for r in results.values() if r is not None])}/{len(raw_ids)}")
    
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single: python process.py <raw_id> [threshold] [--skip-linking]")
        print("  Batch:  python process.py --batch <raw_id1,raw_id2,...> [threshold] [--skip-linking]")
        sys.exit(1)
    
    # Parse arguments
    args = sys.argv[1:]
    
    if args[0] == "--batch":
        # Batch mode
        if len(args) < 2:
            print("Error: --batch requires a comma-separated list of raw_ids")
            sys.exit(1)
        
        raw_ids = args[1].split(",")
        threshold = float(args[2]) if len(args) > 2 and not args[2].startswith("--") else 0.75
        skip_linking = "--skip-linking" in args
        
        batch_process(raw_ids, threshold, skip_linking)
    else:
        # Single mode
        raw_id = args[0]
        threshold = float(args[1]) if len(args) > 1 and not args[1].startswith("--") else 0.75
        skip_linking = "--skip-linking" in args
        
        process_capture(raw_id, threshold, skip_linking)

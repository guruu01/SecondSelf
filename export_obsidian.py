"""
Export wiki notes to Obsidian-compatible markdown format.
Obsidian's native graph view will visualize the connections between notes.
"""
import json
from pathlib import Path
from typing import Dict
from models import WikiNote


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


def export_to_obsidian(output_dir: str = "obsidian_vault") -> None:
    """
    Export wiki notes to Obsidian markdown format.
    
    Args:
        output_dir: Directory to create Obsidian vault.
    """
    wiki_notes = load_wiki_notes()
    vault_path = Path(output_dir)
    vault_path.mkdir(exist_ok=True)
    
    # Create .obsidian directory for config
    obsidian_dir = vault_path / ".obsidian"
    obsidian_dir.mkdir(exist_ok=True)
    
    # Configure graph view settings
    graph_config = {
        "force": {
            "attraction_strength": 0.05,
            "link_length": 100,
            "repulsion_strength": 200
        },
        "filters": {
            "files": "",
            "folders": "",
            "tags": ""
        },
        "groups": [],
        "layout": {
            "component_seed": 412,
            "force": {
                "attraction_strength": 0.05,
                "link_length": 100,
                "repulsion_strength": 200
            },
            "node_size": {
                "centrality": {
                    "enabled": True,
                    "radius": 15
                },
                "min_radius": 5,
                "tag_size": {
                    "enabled": False,
                    "multiplier": 1,
                    "radius": 5
                }
            }
        },
        "node_field": "title",
        "preview": True,
        "show_arrow": True,
        "show_tags": True
    }
    
    with open(obsidian_dir / "graph-analysis.json", 'w', encoding='utf-8') as f:
        json.dump(graph_config, f, indent=2)
    
    # Export each wiki note as a markdown file
    for wiki_id, note in wiki_notes.items():
        # Use summary as filename, fallback to ID
        filename = note.summary[:50] if note.summary else wiki_id
        # Sanitize filename
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()
        if not filename:
            filename = wiki_id
        filename = f"{filename}.md"
        
        filepath = vault_path / filename
        
        # Create frontmatter
        frontmatter = {
            "id": wiki_id,
            "category": note.category,
            "tags": note.tags,
            "created": note.timestamp,
            "links": list(note.links.keys())
        }
        
        # Build markdown content
        content_lines = ["---"]
        for key, value in frontmatter.items():
            if isinstance(value, list):
                content_lines.append(f"{key}:")
                for item in value:
                    content_lines.append(f"  - {item}")
            else:
                content_lines.append(f"{key}: {value}")
        content_lines.append("---")
        content_lines.append("")
        
        # Add title
        content_lines.append(f"# {note.summary or 'Untitled'}")
        content_lines.append("")
        
        # Add category badge
        content_lines.append(f"**Category:** {note.category}")
        content_lines.append("")
        
        # Add tags
        if note.tags:
            content_lines.append("**Tags:**")
            for tag in note.tags:
                content_lines.append(f"#{tag}")
            content_lines.append("")
        
        # Add content
        content_lines.append("## Content")
        content_lines.append("")
        content_lines.append(note.content)
        content_lines.append("")
        
        # Add links section with wikilinks
        if note.links:
            content_lines.append("## Related Notes")
            content_lines.append("")
            for linked_id, similarity in note.links.items():
                # Find linked note to get its title
                linked_note = wiki_notes.get(linked_id)
                if linked_note:
                    linked_title = linked_note.summary[:50] if linked_note.summary else linked_id
                    linked_title = "".join(c for c in linked_title if c.isalnum() or c in (' ', '-', '_')).strip()
                    if not linked_title:
                        linked_title = linked_id
                    # Create wikilink
                    content_lines.append(f"- [[{linked_title}]] (similarity: {similarity:.2f})")
                else:
                    content_lines.append(f"- [[{linked_id}]] (similarity: {similarity:.2f})")
            content_lines.append("")
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_lines))
    
    print(f"Exported {len(wiki_notes)} notes to Obsidian vault: {vault_path.absolute()}")
    print(f"\nTo view in Obsidian:")
    print(f"1. Open Obsidian")
    print(f"2. Open folder: {vault_path.absolute()}")
    print(f"3. Open the Graph view (Ctrl+G or Command+G)")
    print(f"4. You'll see an interactive graph of your knowledge base!")


if __name__ == "__main__":
    export_to_obsidian()

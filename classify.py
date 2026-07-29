"""
Classification module for PARA categorization of raw captures.

Uses LLM to classify content into Projects, Areas, Resources, or Archives.
"""
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List
from llm_client import get_llm_client
from models import RawCapture


def load_prompts() -> Dict[str, Any]:
    """
    Load prompts from config/prompts.json.
    
    Returns:
        Dict containing prompt templates.
    """
    prompts_path = Path("config/prompts.json")
    if not prompts_path.exists():
        raise FileNotFoundError("config/prompts.json not found")
    
    with open(prompts_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def classify_capture(raw_id: str) -> Dict[str, Any]:
    """
    Classify a raw capture using PARA framework.
    
    Args:
        raw_id: UUID of the raw capture to classify.
    
    Returns:
        Dict with classification results:
        {
            "category": "Projects|Areas|Resources|Archives",
            "tags": ["tag1", "tag2", ...],
            "summary": "One-line summary"
        }
"""
    # Load raw capture
    raw_path = Path(f"raw/{raw_id}.json")
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw capture not found: {raw_path}")
    
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    capture = RawCapture.from_json(json.dumps(raw_data))
    
    # Load prompts
    prompts = load_prompts()
    para_prompt = prompts["para_classification"]
    
    # Build prompt with capture content
    user_prompt = para_prompt["user_prompt"].format(
        content=capture.content,
        capture_type=capture.type
    )
    
    # Call LLM
    client = get_llm_client()
    try:
        response = client.call_api(
            prompt=user_prompt,
            system_prompt=para_prompt["system_prompt"],
            temperature=0.3,
            max_tokens=512
        )
        
        # Parse JSON response
        classification = json.loads(response)
        
        # Validate response structure
        required_keys = ["category", "tags", "summary"]
        for key in required_keys:
            if key not in classification:
                raise ValueError(f"Invalid classification response: missing '{key}'")
        
        # Validate category
        valid_categories = ["Projects", "Areas", "Resources", "Archives"]
        if classification["category"] not in valid_categories:
            raise ValueError(f"Invalid category: {classification['category']}")
        
        # Validate tags is a list
        if not isinstance(classification["tags"], list):
            raise ValueError("Tags must be a list")
        
        return classification
    
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response as JSON: {e}")
        print(f"Raw response: {response}")
        # Return fallback classification
        return {
            "category": "Resources",
            "tags": ["unclassified"],
            "summary": capture.content[:100] + "..." if len(capture.content) > 100 else capture.content
        }
    except Exception as e:
        print(f"Classification failed: {e}")
        # Return fallback classification
        return {
            "category": "Resources",
            "tags": ["unclassified"],
            "summary": capture.content[:100] + "..." if len(capture.content) > 100 else capture.content
        }


def batch_classify(raw_ids: List[str], rate_limit_delay: float = 1.0) -> List[Dict[str, Any]]:
    """
    Classify multiple raw captures with rate limiting.
    
    Args:
        raw_ids: List of UUIDs of raw captures to classify.
        rate_limit_delay: Delay between API calls in seconds to avoid rate limits.
    
    Returns:
        List of classification results in same order as input.
    """
    results = []
    cache_file = Path("cache/batch_classify_cache.json")
    
    # Load cache if exists
    cache = {}
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    
    for i, raw_id in enumerate(raw_ids):
        print(f"Processing {i+1}/{len(raw_ids)}: {raw_id}")
        
        # Check cache first
        if raw_id in cache:
            print(f"  Using cached result")
            results.append(cache[raw_id])
            continue
        
        try:
            classification = classify_capture(raw_id)
            results.append(classification)
            
            # Update cache
            cache[raw_id] = classification
            
            # Save cache periodically
            if (i + 1) % 5 == 0:
                cache_file.parent.mkdir(exist_ok=True)
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache, f, indent=2)
            
            # Rate limiting
            if i < len(raw_ids) - 1:
                time.sleep(rate_limit_delay)
        
        except Exception as e:
            print(f"  Error classifying {raw_id}: {e}")
            # Add fallback result
            results.append({
                "category": "Resources",
                "tags": ["unclassified"],
                "summary": "Classification failed"
            })
    
    # Save final cache
    cache_file.parent.mkdir(exist_ok=True)
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)
    
    return results


if __name__ == "__main__":
    # Test classification
    import sys
    
    if len(sys.argv) > 1:
        raw_id = sys.argv[1]
        result = classify_capture(raw_id)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python classify.py <raw_id>")

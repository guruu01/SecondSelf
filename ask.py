"""
RAG-based Q&A module for querying personal knowledge base.

Implements retrieval-augmented generation to answer questions using wiki notes.
"""
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from embeddings import compute_embedding, compute_similarity, load_embedding
from llm_client import get_llm_client
from wiki import load_wiki_note
from db import get_db, WikiNoteDB, db_to_wiki_note, init_db, is_db_available


# Initialize database on import (optional)
init_db()


def embed_question(question: str) -> np.ndarray:
    """
    Embed a user question using the same model as wiki notes.
    
    Args:
        question: User's question text.
    
    Returns:
        numpy array of embedding vectors.
    
    Raises:
        ValueError: If question is empty or invalid.
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    # Preprocess question
    question = question.strip()
    
    # Compute embedding using the same model as notes
    embedding = compute_embedding(question)
    return embedding


def retrieve_relevant_notes(question: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve most relevant wiki notes for a question using semantic similarity.
    
    Args:
        question: User's question text.
        top_k: Number of top relevant notes to return.
    
    Returns:
        List of dictionaries containing note data and similarity scores.
    """
    # Load all wiki notes from database
    if is_db_available():
        db = next(get_db())
        try:
            wiki_notes_db = db.query(WikiNoteDB).all()
        except Exception as e:
            print(f"Warning: Database query failed: {e}")
            wiki_notes_db = []
        finally:
            db.close()
    else:
        wiki_notes_db = []
    
    if not wiki_notes_db:
        return []
    
    # Embed the question
    question_embedding = embed_question(question)
    
    # Load all notes and compute similarities
    notes_with_scores = []
    
    for db_note in wiki_notes_db:
        try:
            # Convert to WikiNote model
            note = db_to_wiki_note(db_note)
            
            # Load embedding from database
            try:
                note_embedding = load_embedding(note.id)
            except FileNotFoundError:
                # Fallback: compute embedding on the fly
                note_embedding = compute_embedding(note.content)
            
            # Compute similarity
            similarity = compute_similarity(question_embedding, note_embedding)
            
            notes_with_scores.append({
                "note": note,
                "score": similarity,
                "id": note.id,
                "content": note.content,
                "summary": note.summary,
                "category": note.category,
                "tags": note.tags
            })
        except Exception as e:
            print(f"Error processing note {db_note.id}: {e}")
            continue
    
    # Sort by similarity score (descending)
    notes_with_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top-k notes
    return notes_with_scores[:top_k]


def build_rag_prompt(question: str, notes: List[Dict[str, Any]]) -> str:
    """
    Build RAG prompt with retrieved notes as context.
    
    Args:
        question: User's question.
        notes: List of retrieved notes with scores.
    
    Returns:
        Formatted prompt string for LLM.
    """
    # Format context from retrieved notes
    context_parts = []
    for i, note_data in enumerate(notes, 1):
        note = note_data["note"]
        score = note_data["score"]
        
        context_part = f"""
Note {i} (Relevance: {score:.2f}):
Category: {note.category}
Tags: {', '.join(note.tags)}
Summary: {note.summary}
Content: {note.content}
"""
        context_parts.append(context_part)
    
    context = "\n".join(context_parts)
    
    # Build prompt with system instructions
    prompt = f"""You are a helpful assistant that answers questions based on the user's personal knowledge base. Use the provided context notes to answer the question accurately.

CONTEXT NOTES:
{context}

QUESTION: {question}

INSTRUCTIONS:
1. Answer the question using ONLY the information from the context notes above.
2. If the context doesn't contain enough information to answer the question, say so clearly.
3. Cite the specific note numbers you used in your answer (e.g., [Note 1], [Note 2]).
4. Be concise but thorough.
5. If multiple notes provide different perspectives, synthesize them.
6. Do not make up information that isn't in the context.

ANSWER:"""
    
    return prompt


def synthesize_answer(prompt: str) -> str:
    """
    Generate answer using LLM with RAG prompt.
    
    Args:
        prompt: RAG prompt with context and question.
    
    Returns:
        Generated answer string.
    
    Raises:
        Exception: If LLM synthesis fails.
    """
    try:
        client = get_llm_client()
        answer = client.call_api(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for more factual answers
            max_tokens=1024,
            system_prompt="You are a knowledgeable assistant that answers questions based on provided context."
        )
        return answer
    except Exception as e:
        raise Exception(f"Failed to synthesize answer: {str(e)}")


def ask(question: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Ask a question and get an answer synthesized from personal notes.
    
    This is the main RAG pipeline: embed question → retrieve notes → build prompt → synthesize answer.
    
    Args:
        question: User's question.
        top_k: Number of top relevant notes to retrieve.
    
    Returns:
        Dictionary containing:
        - answer: Generated answer
        - sources: List of source note IDs with scores
        - confidence: Average similarity score of retrieved notes
        - question: Original question
    """
    # Retrieve relevant notes
    relevant_notes = retrieve_relevant_notes(question, top_k)
    
    if not relevant_notes:
        return {
            "answer": "I couldn't find any relevant notes in your knowledge base to answer this question.",
            "sources": [],
            "confidence": 0.0,
            "question": question
        }
    
    # Build RAG prompt
    prompt = build_rag_prompt(question, relevant_notes)
    
    # Synthesize answer
    try:
        answer = synthesize_answer(prompt)
    except Exception as e:
        # Fallback: return retrieved notes without synthesis
        answer = f"I encountered an error generating an answer: {str(e)}\n\nHere are the most relevant notes I found:\n\n"
        for i, note_data in enumerate(relevant_notes, 1):
            answer += f"{i}. {note_data['summary']} (Relevance: {note_data['score']:.2f})\n"
    
    # Calculate confidence (average similarity score)
    confidence = sum(note["score"] for note in relevant_notes) / len(relevant_notes)
    
    # Extract source information
    sources = [
        {
            "id": note["id"],
            "summary": note["summary"],
            "score": note["score"],
            "category": note["category"]
        }
        for note in relevant_notes
    ]
    
    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
        "question": question
    }


if __name__ == "__main__":
    # Test the ask function
    test_question = "What are the main components of this project?"
    result = ask(test_question)
    
    print(f"Question: {result['question']}")
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nConfidence: {result['confidence']:.2f}")
    print(f"\nSources:")
    for source in result['sources']:
        print(f"  - {source['summary']} ({source['score']:.2f})")

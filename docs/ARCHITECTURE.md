# SecondSelf — Architecture Document

## 1. System Overview

SecondSelf is a personal AI second brain that captures, organizes, visualizes, and queries personal knowledge. The system follows a pipeline architecture where each component transforms data through successive stages:

```
Capture → Classify → Link → Visualize → Query → Deploy
```

### 1.1 Core Philosophy
- **Zero-friction capture**: Single command for any input type
- **AI-first organization**: Automated PARA classification and linking
- **Visual exploration**: Interactive knowledge graph
- **Natural language interface**: RAG-based Q&A over personal knowledge
- **Public accessibility**: Deployed web application

### 1.2 System Boundaries
- **Input**: Notes, links, files (any text-based content)
- **Output**: Organized wiki, interactive graph, natural language answers
- **Scale**: Personal knowledge base (hundreds to thousands of notes)
- **Deployment**: Cloud-hosted Streamlit application

---

## 2. Technology Stack

### 2.1 Backend (Python)
- **Python 3.10+**: Core language
- **Groq API**: Free LLM for classification and synthesis (Llama 3)
- **sentence-transformers**: Local embeddings (all-MiniLM-L6-v2)
- **numpy**: Vector operations for similarity computation
- **python-dotenv**: Environment variable management

### 2.2 Frontend
- **Streamlit**: Web application framework
- **vis-network / Cytoscape.js**: Interactive graph visualization
- **Streamlit components**: Custom graph integration

### 2.3 Data Storage
- **Filesystem**: JSON and markdown files
- **raw/**: Unprocessed captures with metadata
- **wiki/**: Processed, classified, linked notes
- **graph.json**: Serialized graph structure

### 2.4 Deployment
- **Streamlit Cloud** or **HuggingFace Spaces**: Free hosting
- **GitHub**: Version control and public repository

### 2.5 Development
- **pytest**: Testing framework
- **black**: Code formatting
- **pre-commit**: Git hooks

---

## 3. Data Architecture

### 3.1 Data Models

#### 3.1.1 Raw Capture (raw/)
```json
{
  "id": "uuid-v4",
  "timestamp": "ISO-8601",
  "type": "note|link|file",
  "content": "string",
  "source": "string (optional)",
  "metadata": {
    "original_filename": "string (optional)",
    "url": "string (optional)",
    "file_type": "string (optional)"
  }
}
```

#### 3.1.2 Wiki Note (wiki/)
```json
{
  "id": "uuid-v4",
  "timestamp": "ISO-8601",
  "raw_id": "uuid-v4",
  "content": "string",
  "category": "Projects|Areas|Resources|Archives",
  "tags": ["string"],
  "summary": "string",
  "links": ["uuid-v4"],
  "embedding": [float_array],
  "metadata": {
    "classification_confidence": "float",
    "link_confidence": "float"
  }
}
```

#### 3.1.3 Graph Data (graph.json)
```json
{
  "nodes": [
    {
      "id": "uuid-v4",
      "label": "string",
      "title": "string (hover content)",
      "category": "string",
      "tags": ["string"],
      "size": "number",
      "color": "string"
    }
  ],
  "edges": [
    {
      "from": "uuid-v4",
      "to": "uuid-v4",
      "weight": "float",
      "title": "string (similarity score)"
    }
  ]
}
```

### 3.2 Storage Architecture

```
secondself/
├── raw/                          # Week 1: Unprocessed captures
│   ├── {uuid}.json              # Individual capture files
│   └── index.json               # Master index of all captures
├── wiki/                         # Week 2: Processed notes
│   ├── {uuid}.json              # Individual wiki notes
│   ├── embeddings/              # Cached embeddings
│   │   └── {uuid}.npy
│   └── index.json               # Master index with links
├── graph.json                    # Week 3: Serialized graph
├── cache/                        # Temporary processing cache
└── config/                       # Configuration files
    ├── prompts.json             # LLM prompts
    └── thresholds.json          # Similarity thresholds
```

### 3.3 Data Flow

```
User Input
    ↓
[capture.py] → raw/{uuid}.json
    ↓
[classify.py] → PARA category + tags + summary
    ↓
[link.py] → Embeddings + similarity computation
    ↓
wiki/{uuid}.json (with links)
    ↓
[build_graph.py] → graph.json
    ↓
[app.py] → Interactive visualization + RAG query
    ↓
User Interface (Streamlit)
```

---

## 4. Component Architecture

### 4.1 Week 1: The Archivist (Capture Pipeline)

#### 4.1.1 capture.py
**Responsibility**: Universal capture interface for any content type

**Functions**:
- `capture_note(content: str, source: str = None) -> str`
- `capture_link(url: str) -> str`
- `capture_file(file_path: str) -> str`
- `generate_uuid() -> str`
- `get_timestamp() -> str`

**Input**: Note text, URL, or file path
**Output**: UUID of saved capture
**Side Effects**: Creates file in raw/, updates index

**Error Handling**:
- Invalid file types
- Network failures for links
- Filesystem permissions

---

### 4.2 Week 2: The Librarian (Auto-Organization)

#### 4.2.1 classify.py
**Responsibility**: AI-powered PARA classification and metadata extraction

**Functions**:
- `classify_capture(raw_id: str) -> dict`
- `batch_classify(raw_ids: List[str]) -> List[dict]`
- `build_para_prompt(content: str) -> str`
- `parse_llm_response(response: str) -> dict`

**Input**: Raw capture ID or content
**Output**: Category, tags, summary
**External Dependencies**: Groq API (Llama 3)

**PARA Framework**:
- **Projects**: Active work with deadlines
- **Areas**: Ongoing responsibilities
- **Resources**: Reference material
- **Archives**: Completed or inactive items

**Error Handling**:
- API rate limits
- Invalid LLM responses
- Timeout handling

#### 4.2.2 link.py
**Responsibility**: Semantic similarity computation and auto-linking

**Functions**:
- `compute_embedding(text: str) -> np.ndarray`
- `compute_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float`
- `find_related_notes(new_embedding: np.ndarray, threshold: float = 0.75) -> List[str]`
- `auto_link(wiki_id: str) -> List[str]`
- `batch_link(wiki_ids: List[str]) -> None`

**Input**: Wiki note ID
**Output**: List of related note IDs
**Model**: sentence-transformers (all-MiniLM-L6-v2)

**Similarity Thresholds**:
- Strong link: > 0.85
- Moderate link: 0.75 - 0.85
- Weak link: 0.65 - 0.75 (configurable)

**Performance Considerations**:
- Cache embeddings in wiki/embeddings/
- Batch similarity computation for efficiency
- Use cosine similarity

---

### 4.3 Week 3: The Cartographer (Visualization)

#### 4.3.1 build_graph.py
**Responsibility**: Convert wiki structure to graph representation

**Functions**:
- `build_nodes() -> List[dict]`
- `build_edges() -> List[dict]`
- `calculate_node_size(wiki_id: str) -> int`
- `assign_node_color(category: str) -> str`
- `export_graph(output_path: str) -> None`

**Input**: Wiki directory
**Output**: graph.json

**Node Attributes**:
- Size based on link count (centrality)
- Color based on PARA category
- Label based on summary or title

**Edge Attributes**:
- Weight based on similarity score
- Direction: bidirectional for related notes

#### 4.3.2 Graph Visualization (Streamlit Component)
**Responsibility**: Render interactive knowledge graph

**Technology**: vis-network (via Streamlit custom component)

**Features**:
- Force-directed layout
- Hover tooltips with note content
- Drag-and-drop node positioning
- Zoom and pan
- Click to view full note
- Filter by category/tags

**Configuration**:
- Physics parameters (repulsion, spring length)
- Color scheme per category
- Node size range

---

### 4.4 Week 4: The Oracle (Query & Deployment)

#### 4.4.1 ask.py
**Responsibility**: Retrieval-augmented generation for natural language Q&A

**Functions**:
- `ask(question: str, top_k: int = 5) -> str`
- `retrieve_relevant_notes(question: str, top_k: int) -> List[dict]`
- `build_rag_prompt(question: str, notes: List[dict]) -> str`
- `synthesize_answer(prompt: str) -> str`

**Pipeline**:
1. Embed user question
2. Compute similarity with all wiki notes
3. Retrieve top-k most relevant notes
4. Build context prompt with retrieved notes
5. Send to LLM for answer synthesis
6. Return answer with source citations

**Input**: Natural language question
**Output**: Answer with source references
**External Dependencies**: Groq API, sentence-transformers

**Citation Format**:
- Inline references to note IDs
- Confidence scores
- Link to original note

#### 4.4.2 app.py (Streamlit Application)
**Responsibility**: Unified web interface

**Components**:
- **Sidebar**: Capture interface, statistics, filters
- **Main Area**: Tabbed interface
  - Tab 1: Interactive Graph
  - Tab 2: Ask Your Brain (search)
  - Tab 3: Browse Wiki
- **Capture Panel**: Input forms for notes/links/files
- **Search Panel**: Question input and answer display

**State Management**:
- Streamlit session state for graph filters
- Cached embeddings and graph data
- Real-time capture processing

**User Flow**:
1. User captures content via sidebar
2. System auto-processes (classify + link)
3. Graph updates automatically
4. User explores graph or asks questions
5. Answers returned with source citations

---

## 5. API Interfaces

### 5.1 Module Contracts

#### 5.1.1 Capture Module
```python
def capture(content: str, type: str = "note", **kwargs) -> str:
    """
    Capture any content into the system.
    
    Args:
        content: The content to capture
        type: One of "note", "link", "file"
        **kwargs: Additional metadata (url, file_path, etc.)
    
    Returns:
        UUID of the captured item
    
    Raises:
        ValueError: Invalid type or content
        IOError: Filesystem error
    """
```

#### 5.1.2 Classification Module
```python
def classify(raw_id: str) -> dict:
    """
    Classify a raw capture using PARA framework.
    
    Args:
        raw_id: UUID of raw capture
    
    Returns:
        {
            "category": "Projects|Areas|Resources|Archives",
            "tags": ["tag1", "tag2"],
            "summary": "One-line summary"
        }
    
    Raises:
        KeyError: Raw capture not found
        APIError: LLM API failure
    """
```

#### 5.1.3 Linking Module
```python
def link(wiki_id: str, threshold: float = 0.75) -> List[str]:
    """
    Find and link related notes using embeddings.
    
    Args:
        wiki_id: UUID of wiki note to link
        threshold: Similarity threshold (0-1)
    
    Returns:
        List of related note UUIDs
    
    Raises:
        KeyError: Wiki note not found
    """
```

#### 5.1.4 Query Module
```python
def ask(question: str, top_k: int = 5) -> dict:
    """
    Answer a question using RAG over personal knowledge.
    
    Args:
        question: Natural language question
        top_k: Number of notes to retrieve
    
    Returns:
        {
            "answer": "Synthesized answer",
            "sources": [{"id": "uuid", "snippet": "content", "score": 0.9}],
            "confidence": 0.85
        }
    
    Raises:
        ValueError: Empty question
        APIError: LLM API failure
    """
```

---

## 6. Deployment Architecture

### 6.1 Local Development
```
Environment: Python 3.10+
Virtual Environment: venv or conda
Configuration: .env file with API keys
Data: Local filesystem (raw/, wiki/)
```

### 6.2 Cloud Deployment (Streamlit Cloud)

#### 6.2.1 Repository Structure
```
secondself/
├── .streamlit/
│   └── config.toml              # Streamlit configuration
├── raw/                         # Git LFS for large files
├── wiki/
├── graph.json
├── capture.py
├── classify.py
├── link.py
├── build_graph.py
├── ask.py
├── app.py
├── requirements.txt
├── .env                         # Secrets (not committed)
├── .gitignore
└── README.md
```

#### 6.2.2 Deployment Pipeline
1. Push to GitHub
2. Connect Streamlit Cloud to repository
3. Configure environment variables (Groq API key)
4. Deploy automatically on push
5. Public URL: `https://secondself-user.streamlit.app`

#### 6.2.3 Environment Variables
- `GROQ_API_KEY`: Groq API key for LLM access
- `SIMILARITY_THRESHOLD`: Default similarity threshold
- `TOP_K_RESULTS`: Default retrieval count

### 6.3 Alternative Deployment (HuggingFace Spaces)
```
Platform: HuggingFace Spaces
Framework: Streamlit
Hardware: CPU Basic (free tier)
Storage: Git-based repository
```

---

## 7. Performance & Scalability

### 7.1 Performance Targets
- **Capture latency**: < 1 second (local), < 3 seconds (with classification)
- **Classification latency**: < 5 seconds per note
- **Linking latency**: < 2 seconds per note (with cached embeddings)
- **Graph rendering**: < 3 seconds for 500 nodes
- **Query latency**: < 5 seconds (retrieval + synthesis)

### 7.2 Scalability Considerations
- **Embedding cache**: Store computed embeddings to avoid recomputation
- **Batch processing**: Process multiple captures in parallel
- **Lazy loading**: Load graph data on demand for large knowledge bases
- **Pagination**: Limit graph rendering to top N nodes by centrality

### 7.3 Optimization Strategies
- Use faiss or annoy for approximate nearest neighbor search (if scale > 1000 notes)
- Implement incremental graph updates (don't rebuild entire graph on each capture)
- Cache LLM responses for similar classification tasks
- Use async I/O for API calls

---

## 8. Security & Privacy

### 8.1 Data Privacy
- All data stored locally by default
- No data sent to third parties except:
  - Content to Groq API for classification/synthesis
  - Content to sentence-transformers (local model)
- API keys stored in environment variables, never committed

### 8.2 Security Measures
- Input sanitization for file uploads
- Rate limiting for API calls
- Validation of all user inputs
- Secure handling of API credentials

### 8.3 Deployment Security
- Streamlit Cloud secrets management
- HTTPS enforced
- No authentication required (public read-only)
- Optional: Add authentication for private deployments

---

## 9. Testing Strategy

### 9.1 Unit Tests
- Test capture functions with various input types
- Test classification with mock LLM responses
- Test embedding computation
- Test similarity calculations
- Test graph building logic

### 9.2 Integration Tests
- End-to-end capture → classify → link pipeline
- Graph rendering with sample data
- RAG query with known questions
- Streamlit app component integration

### 9.3 Manual Testing
- Test with 10+ real captures (Week 1)
- Test with 15+ real items for organization (Week 2)
- Test graph with real personal knowledge (Week 3)
- Test queries with real questions (Week 4)

---

## 10. Monitoring & Observability

### 10.1 Logging
- Capture operations with timestamps
- Classification results and confidence scores
- Linking operations and similarity scores
- Query logs with question-answer pairs
- Error logs with stack traces

### 10.2 Metrics
- Number of captures over time
- Classification accuracy (manual spot-check)
- Average number of links per note
- Query response times
- User engagement (if deployed publicly)

### 10.3 Debugging
- Streamlit debug mode for development
- Verbose logging for pipeline steps
- Intermediate data inspection (raw captures, embeddings)
- Graph visualization for link validation

---

## 11. Future Enhancements

### 11.1 Potential Features
- **Multi-modal support**: Image and audio capture
- **Advanced graph layouts**: Hierarchical, temporal
- **Collaboration**: Share brains with others
- **Mobile app**: iOS/Android capture interface
- **Browser extension**: One-click capture from web
- **Advanced RAG**: Hybrid search (semantic + keyword)
- **Knowledge extraction**: Auto-generate insights and summaries
- **Backup/sync**: Cloud storage integration

### 11.2 Technical Improvements
- **Database backend**: SQLite or PostgreSQL for larger scale
- **Vector database**: Chroma or Pinecone for embeddings
- **Caching layer**: Redis for frequently accessed data
- **API server**: FastAPI for headless operation
- **Webhooks**: Trigger processing on capture

---

## 12. Development Workflow

### 12.1 Week-by-Week Implementation
1. **Week 1**: Scaffold project, implement capture.py, test with 10+ items
2. **Week 2**: Implement classify.py and link.py, process 15+ items
3. **Week 3**: Implement build_graph.py and graph visualization
4. **Week 4**: Implement ask.py and app.py, deploy to public URL

### 12.2 Git Workflow
- Main branch: stable deployment
- Feature branches: weekly milestones
- Pull requests: code review before merge
- Tags: version releases (v0.1.0, v0.2.0, etc.)

### 12.3 Code Quality
- Black formatting for all Python code
- Type hints for function signatures
- Docstrings for all public functions
- PEP 8 compliance
- Pre-commit hooks for quality checks

---

## 13. Risks & Mitigations

### 13.1 Technical Risks
- **Risk**: Groq API rate limits or downtime
  - **Mitigation**: Implement fallback to local models, queue requests

- **Risk**: Embedding model performance degradation
  - **Mitigation**: Use established models, benchmark alternatives

- **Risk**: Graph rendering performance with large datasets
  - **Mitigation**: Implement pagination, lazy loading, WebGL acceleration

### 13.2 Project Risks
- **Risk**: Scope creep in Week 4 (UI integration)
  - **Mitigation**: Keep UI simple, prioritize functionality over polish

- **Risk**: Deployment platform limitations
  - **Mitigation**: Have backup deployment options (HF Spaces, Railway)

- **Risk**: Data loss during development
  - **Mitigation**: Regular backups, git for code, copy of raw/ directory

---

## 14. Success Criteria

### 14.1 Functional Requirements
- ✅ Capture any note, link, or file with single command
- ✅ Auto-classify using PARA framework
- ✅ Auto-link related notes using embeddings
- ✅ Render interactive knowledge graph
- ✅ Answer natural language questions using RAG
- ✅ Deploy to public URL

### 14.2 Non-Functional Requirements
- ✅ Response time < 5 seconds for all operations
- ✅ Handle 1000+ notes without performance degradation
- ✅ Clean, maintainable codebase
- ✅ Comprehensive documentation
- ✅ Public GitHub repository with README

---

## 15. Architecture Diagrams

### 15.1 High-Level System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                           │
│                    (Streamlit App)                           │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Capture    │  │  Graph View  │  │   Search     │      │
│  │   Interface  │  │              │  │   Interface  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
┌─────────┼─────────────────┼─────────────────┼──────────────┐
│         ▼                 ▼                 ▼               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  capture.py  │  │build_graph.py│  │   ask.py     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
┌─────────┼─────────────────┼─────────────────┼──────────────┐
│         ▼                 ▼                 ▼               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │classify.py   │  │  link.py     │  │  RAG Engine  │      │
│  │(Groq API)    │  │(Embeddings)  │  │(Groq API)    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
┌─────────┴─────────────────┴─────────────────┴──────────────┐
│                     Data Storage Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │   raw/   │  │  wiki/   │  │embeddings│  │ graph.json │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 15.2 Data Flow Pipeline
```
┌─────────┐
│  Input  │ (Note/Link/File)
└────┬────┘
     │
     ▼
┌──────────────┐
│ capture.py   │ → Generate UUID, timestamp
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ raw/{id}.json│ → Store with metadata
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ classify.py   │ → Groq API → PARA + tags + summary
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ link.py      │ → Embeddings → Similarity → Links
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ wiki/{id}.json│ → Classified + linked note
└──────┬───────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌──────────────┐ ┌──────────────┐
│build_graph.py│ │   ask.py     │
└──────┬───────┘ └──────┬───────┘
       │               │
       ▼               ▼
┌──────────────┐ ┌──────────────┐
│ graph.json   │ │  RAG Answer  │
└──────┬───────┘ └──────┬───────┘
       │               │
       └───────┬───────┘
               │
               ▼
      ┌──────────────┐
      │  Streamlit   │
      │     UI       │
      └──────────────┘
```

---

## 16. Configuration Files

### 16.1 requirements.txt
```
streamlit>=1.28.0
sentence-transformers>=2.2.0
numpy>=1.24.0
groq>=0.4.0
python-dotenv>=1.0.0
vis-network>=0.1.0
pytest>=7.4.0
black>=23.0.0
```

### 16.2 .streamlit/config.toml
```toml
[theme]
primaryColor = "#F63366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = true
maxUploadSize = 200

[logger]
level = "info"
```

### 16.3 .env.example
```
GROQ_API_KEY=your_groq_api_key_here
SIMILARITY_THRESHOLD=0.75
TOP_K_RESULTS=5
```

---

## 17. Conclusion

This architecture provides a comprehensive blueprint for building SecondSelf, a personal AI second brain. The modular design allows for incremental development across the 4-week timeline while maintaining flexibility for future enhancements.

Key architectural decisions:
- **Filesystem-based storage**: Simple, portable, no database complexity
- **Free AI services**: Groq for LLM, sentence-transformers for embeddings
- **Streamlit for UI**: Rapid development, easy deployment
- **Pipeline architecture**: Clear separation of concerns
- **RAG for queries**: Leverages personal knowledge effectively

The system prioritizes simplicity and usability while providing powerful AI-driven organization and retrieval capabilities.

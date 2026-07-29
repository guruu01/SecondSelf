# SecondSelf — Phase-wise Implementation Plan

## Overview

This implementation plan breaks down the SecondSelf project into 4 phases (weeks), each corresponding to a milestone from the problem statement. Each phase includes specific tasks, deliverables, acceptance criteria, and time estimates.

**Total Timeline**: 4 weeks
**Development Approach**: Incremental, test-driven, with real data validation
**Deployment**: Public URL by end of Phase 4

---

## Phase 1: The Archivist — "Capture Everything, Lose Nothing"

**Duration**: Week 1
**Objective**: Build universal capture pipeline for any content type
**Badge**: The Archivist

### 1.1 Tasks

#### Task 1.1: Project Scaffold
**Time**: 2 hours
**Description**: Set up project structure and development environment

**Subtasks**:
- Create directory structure: `raw/`, `wiki/`, `cache/`, `config/`
- Initialize Python virtual environment
- Create `requirements.txt` with initial dependencies
- Set up `.gitignore` for Python projects
- Create `.env.example` template
- Initialize git repository

**Deliverables**:
- Directory structure created
- `requirements.txt` with: `python-dotenv`, `uuid`, `datetime`, `json`, `pathlib`
- `.gitignore` configured
- Virtual environment activated

**Acceptance Criteria**:
- [ ] `raw/` and `wiki/` directories exist
- [ ] Virtual environment is active
- [ ] `requirements.txt` is committed
- [ ] `.gitignore` excludes `__pycache__`, `.env`, `*.pyc`

---

#### Task 1.2: UUID and Timestamp Utilities
**Time**: 1 hour
**Description**: Implement helper functions for unique identification

**Subtasks**:
- Create `utils.py` module
- Implement `generate_uuid()` using Python's `uuid` module
- Implement `get_timestamp()` returning ISO-8601 format
- Add unit tests for both functions

**Deliverables**:
- `utils.py` with UUID and timestamp functions
- Unit tests in `tests/test_utils.py`

**Acceptance Criteria**:
- [ ] `generate_uuid()` returns unique UUID v4
- [ ] `get_timestamp()` returns valid ISO-8601 string
- [ ] Unit tests pass

---

#### Task 1.3: Raw Capture Data Model
**Time**: 1 hour
**Description**: Define and implement raw capture JSON structure

**Subtasks**:
- Define raw capture schema (from architecture)
- Create `models.py` with data classes
- Implement validation for capture types
- Add JSON serialization/deserialization

**Deliverables**:
- `models.py` with `RawCapture` dataclass
- Schema validation functions

**Acceptance Criteria**:
- [ ] Raw capture includes: id, timestamp, type, content, source, metadata
- [ ] Type validation accepts: "note", "link", "file"
- [ ] JSON serialization/deserialization works correctly

---

#### Task 1.4: Note Capture Function
**Time**: 2 hours
**Description**: Implement capture functionality for text notes

**Subtasks**:
- Implement `capture_note(content: str, source: str = None) -> str`
- Generate UUID and timestamp
- Create JSON file in `raw/` directory
- Update master index in `raw/index.json`
- Add error handling for empty content

**Deliverables**:
- `capture_note()` function in `capture.py`
- Index management functions
- Error handling

**Acceptance Criteria**:
- [ ] Function returns UUID of saved capture
- [ ] JSON file created in `raw/` with correct structure
- [ ] Index updated with new capture
- [ ] Empty content raises ValueError

---

#### Task 1.5: Link Capture Function
**Time**: 2 hours
**Description**: Implement capture functionality for URLs

**Subtasks**:
- Implement `capture_link(url: str) -> str`
- Validate URL format
- Fetch page title (optional, using requests)
- Store URL in metadata
- Handle network errors gracefully

**Deliverables**:
- `capture_link()` function in `capture.py`
- URL validation
- Network error handling

**Acceptance Criteria**:
- [ ] Invalid URLs raise ValueError
- [ ] Network errors handled gracefully
- [ ] URL stored in metadata
- [ ] Returns UUID of saved capture

---

#### Task 1.6: File Capture Function
**Time**: 2 hours
**Description**: Implement capture functionality for file uploads

**Subtasks**:
- Implement `capture_file(file_path: str) -> str`
- Validate file exists and is readable
- Extract file content (text files only for now)
- Store original filename in metadata
- Handle binary files (store reference only)

**Deliverables**:
- `capture_file()` function in `capture.py`
- File validation
- Content extraction for text files

**Acceptance Criteria**:
- [ ] Non-existent files raise FileNotFoundError
- [ ] Text file content extracted and stored
- [ ] Original filename preserved in metadata
- [ ] Returns UUID of saved capture

---

#### Task 1.7: Unified Capture Interface
**Time**: 1 hour
**Description**: Create single entry point for all capture types

**Subtasks**:
- Implement `capture(content: str, type: str = "note", **kwargs) -> str`
- Route to appropriate capture function based on type
- Add comprehensive error handling
- Create CLI wrapper for command-line usage

**Deliverables**:
- Unified `capture()` function
- CLI interface in `__main__.py`
- Usage documentation

**Acceptance Criteria**:
- [ ] Single function handles all capture types
- [ ] Type validation works correctly
- [ ] CLI can be run: `python -m capture "my note"`
- [ ] CLI can capture files and links

---

#### Task 1.8: Testing with Real Data
**Time**: 3 hours
**Description**: Validate capture pipeline with 10+ real items

**Subtasks**:
- Capture 10+ real personal items (notes, links, files)
- Verify all captures have UUIDs and timestamps
- Verify index is correctly maintained
- Test edge cases (very long notes, special characters)

**Deliverables**:
- `raw/` directory with 10+ real captures
- Test report documenting edge cases

**Acceptance Criteria**:
- [ ] 10+ real items captured successfully
- [ ] All items have unique UUIDs
- [ ] All items have valid timestamps
- [ ] Index correctly lists all captures
- [ ] Edge cases handled without errors

---

### 1.2 Phase 1 Deliverables

**Primary Deliverable**: "Ship the Capture Pipeline"
- Working capture script — one command saves anything to `raw/` with timestamp + unique ID
- `raw/` folder populated with 10+ real captured items (not test data)
- 🏅 Badge: The Archivist

### 1.3 Phase 1 Acceptance Criteria

- [ ] `raw/` and `wiki/` folder structure exists
- [ ] One command captures a note, a link, AND a file
- [ ] Every capture has a timestamp + unique ID
- [ ] 10+ real items captured

### 1.4 Phase 1 Success Metrics

- **Functional**: All three capture types work correctly
- **Quality**: Zero data loss in 10+ test captures
- **Usability**: Single command interface works
- **Code**: Unit tests pass, code follows PEP 8

---

## Phase 2: The Librarian — "Teach AI to Organize For You"

**Duration**: Week 2
**Objective**: Implement AI-powered PARA classification and auto-linking
**Badge**: The Librarian

### 2.1 Tasks

#### Task 2.1: Groq API Integration
**Time**: 2 hours
**Description**: Set up Groq API client for LLM access

**Subtasks**:
- Install `groq` Python package
- Set up API key in `.env`
- Create `llm_client.py` module
- Implement basic API call wrapper
- Add error handling and retry logic
- Test API connectivity

**Deliverables**:
- `llm_client.py` with Groq integration
- API key configuration
- Connection test

**Acceptance Criteria**:
- [ ] Groq API client initialized successfully
- [ ] API call wrapper handles errors
- [ ] Retry logic implemented for rate limits
- [ ] Test call to Llama 3 succeeds

---

#### Task 2.2: PARA Classification Prompt Engineering
**Time**: 2 hours
**Description**: Design and implement prompts for PARA classification

**Subtasks**:
- Research PARA framework (Projects, Areas, Resources, Archives)
- Create classification prompt template
- Design output format for structured parsing
- Create few-shot examples in prompt
- Test prompt with sample content

**Deliverables**:
- `config/prompts.json` with classification prompt
- Prompt testing results

**Acceptance Criteria**:
- [ ] Prompt clearly defines PARA categories
- [ ] Output format is parseable (JSON)
- [ ] Few-shot examples improve accuracy
- [ ] Manual testing shows reasonable classifications

---

#### Task 2.3: Classification Function
**Time**: 3 hours
**Description**: Implement classification logic for raw captures

**Subtasks**:
- Implement `classify_capture(raw_id: str) -> dict`
- Load raw capture from `raw/`
- Build prompt with capture content
- Call Groq API
- Parse LLM response into structured data
- Handle parsing errors gracefully

**Deliverables**:
- `classify_capture()` function in `classify.py`
- Response parser
- Error handling

**Acceptance Criteria**:
- [ ] Returns category (Projects/Areas/Resources/Archives)
- [ ] Returns list of tags
- [ ] Returns one-line summary
- [ ] Invalid responses handled gracefully
- [ ] API errors trigger retry or fallback

---

#### Task 2.4: Batch Classification
**Time**: 2 hours
**Description**: Implement batch processing for multiple captures

**Subtasks**:
- Implement `batch_classify(raw_ids: List[str]) -> List[dict]`
- Add progress tracking
- Implement rate limiting to avoid API limits
- Save intermediate results
- Add resume capability for interrupted batches

**Deliverables**:
- `batch_classify()` function
- Progress tracking
- Rate limiting

**Acceptance Criteria**:
- [ ] Processes multiple captures sequentially
- [ ] Rate limiting prevents API errors
- [ ] Progress displayed to user
- [ ] Interrupted batches can be resumed

---

#### Task 2.5: Wiki Note Data Model
**Time**: 1 hour
**Description**: Define wiki note structure with classification data

**Subtasks**:
- Create `WikiNote` dataclass in `models.py`
- Include fields: id, timestamp, raw_id, content, category, tags, summary, links, embedding
- Add validation for PARA categories
- Implement JSON serialization

**Deliverables**:
- `WikiNote` dataclass
- Validation functions
- Serialization

**Acceptance Criteria**:
- [ ] All required fields present
- [ ] Category validation works
- [ ] JSON serialization/deserialization correct

---

#### Task 2.6: Wiki Creation Pipeline
**Time**: 2 hours
**Description**: Transform classified raw captures into wiki notes

**Subtasks**:
- Implement `create_wiki_note(raw_id: str, classification: dict) -> str`
- Copy content from raw capture
- Add classification metadata
- Generate new UUID for wiki note
- Save to `wiki/` directory
- Update wiki index

**Deliverables**:
- Wiki creation function
- Index management
- Transformation logic

**Acceptance Criteria**:
- [ ] Wiki note created in `wiki/`
- [ ] Classification data preserved
- [ ] Link to raw capture maintained
- [ ] Index updated correctly

---

#### Task 2.7: Sentence-Transformers Integration
**Time**: 2 hours
**Description**: Set up local embedding model

**Subtasks**:
- Install `sentence-transformers` and `numpy`
- Download `all-MiniLM-L6-v2` model
- Create `embeddings.py` module
- Implement `compute_embedding(text: str) -> np.ndarray`
- Add model caching to avoid re-downloading

**Deliverables**:
- `embeddings.py` with embedding computation
- Model download script
- Caching logic

**Acceptance Criteria**:
- [ ] Model downloads successfully
- [ ] Embedding computation works
- [ ] Returns numpy array of correct dimension
- [ ] Model cached locally

---

#### Task 2.8: Similarity Computation
**Time**: 2 hours
**Description**: Implement semantic similarity between embeddings

**Subtasks**:
- Implement `compute_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float`
- Use cosine similarity
- Add batch similarity computation
- Optimize with numpy operations

**Deliverables**:
- Similarity computation function
- Batch processing
- Performance optimization

**Acceptance Criteria**:
- [ ] Returns similarity score between 0 and 1
- [ ] Cosine similarity implemented correctly
- [ ] Batch computation faster than individual
- [ ] Handles different array dimensions

---

#### Task 2.9: Auto-Linking Logic
**Time**: 3 hours
**Description**: Find and link related notes automatically

**Subtasks**:
- Implement `find_related_notes(new_embedding: np.ndarray, threshold: float = 0.75) -> List[str]`
- Load all existing wiki embeddings
- Compute similarities
- Filter by threshold
- Return sorted list of related note IDs
- Add confidence scores

**Deliverables**:
- Related notes finder
- Threshold filtering
- Confidence scoring

**Acceptance Criteria**:
- [ ] Finds notes above similarity threshold
- [ ] Returns sorted by similarity score
- [ ] Configurable threshold works
- [ ] Handles empty wiki gracefully

---

#### Task 2.10: Embedding Caching
**Time**: 2 hours
**Description**: Cache embeddings to avoid recomputation

**Subtasks**:
- Create `wiki/embeddings/` directory
- Save embeddings as `.npy` files
- Implement cache lookup before computation
- Add cache invalidation option
- Update wiki note with embedding reference

**Deliverables**:
- Embedding cache system
- Cache management functions
- Integration with wiki notes

**Acceptance Criteria**:
- [ ] Embeddings saved to `wiki/embeddings/`
- [ ] Cache hit avoids recomputation
- [ ] Cache can be invalidated
- [ ] Wiki notes reference cached embeddings

---

#### Task 2.11: Auto-Link Integration
**Time**: 2 hours
**Description**: Integrate auto-linking into wiki creation pipeline

**Subtasks**:
- Implement `auto_link(wiki_id: str) -> List[str]`
- Compute embedding for new note
- Find related notes
- Add links to wiki note
- Update linked notes with reciprocal links
- Save updated wiki notes

**Deliverables**:
- Auto-link function
- Reciprocal linking
- Wiki note updates

**Acceptance Criteria**:
- [ ] New note linked to related notes
- [ ] Related notes updated with reciprocal links
- [ ] Links stored in wiki note metadata
- [ ] Similarity threshold respected

---

#### Task 2.12: Batch Linking
**Time**: 2 hours
**Description**: Process multiple notes for linking

**Subtasks**:
- Implement `batch_link(wiki_ids: List[str]) -> None`
- Process notes sequentially
- Update graph incrementally
- Handle linking errors gracefully
- Add progress tracking

**Deliverables**:
- Batch linking function
- Progress tracking
- Error handling

**Acceptance Criteria**:
- [ ] Processes multiple notes
- [ ] Progress displayed
- [ ] Errors don't stop entire batch
- [ ] Links created correctly

---

#### Task 2.13: End-to-End Pipeline Integration
**Time**: 2 hours
**Description**: Combine classification and linking into single pipeline

**Subtasks**:
- Create `process_capture(raw_id: str) -> str` function
- Chain classification → wiki creation → linking
- Add logging at each step
- Implement error recovery
- Create CLI command for pipeline

**Deliverables**:
- Integrated pipeline function
- CLI command
- Logging system

**Acceptance Criteria**:
- [ ] Single function processes raw to wiki
- [ ] All steps execute in order
- [ ] Errors logged appropriately
- [ ] CLI command works: `python -m process <raw_id>`

---

#### Task 2.14: Testing with Real Data
**Time**: 3 hours
**Description**: Validate pipeline with 15+ real items

**Subtasks**:
- Process 15+ real captures from Phase 1
- Verify PARA classifications are reasonable
- Verify links make semantic sense
- Check embeddings are computed correctly
- Validate wiki structure

**Deliverables**:
- `wiki/` directory with 15+ processed notes
- Classification quality report
- Linking quality report

**Acceptance Criteria**:
- [ ] 15+ real items processed
- [ ] Classifications follow PARA framework
- [ ] Links connect semantically related notes
- [ ] No broken links in wiki
- [ ] Embeddings cached correctly

---

### 2.2 Phase 2 Deliverables

**Primary Deliverable**: "Ship the Self-Organizing Wiki"
- Pipeline that auto-classifies raw captures with PARA and auto-links related notes
- Run on 15+ real items → organized `wiki/` folder with linked notes
- 🏅 Badge: The Librarian

### 2.3 Phase 2 Acceptance Criteria

- [ ] Any raw capture → category + tags + summary automatically
- [ ] PARA categorization working
- [ ] Embeddings computed per note
- [ ] Related notes auto-linked (no manual tagging)
- [ ] Runs on 15+ real items → organized wiki/

### 2.4 Phase 2 Success Metrics

- **Functional**: Classification accuracy > 80% (manual spot-check)
- **Quality**: Links make semantic sense
- **Performance**: Processing time < 10 seconds per note
- **Code**: All modules tested, error handling robust

---

## Phase 3: The Cartographer — "Visualize the Brain"

**Duration**: Week 3
**Objective**: Build interactive knowledge graph visualization
**Badge**: The Cartographer

### 3.1 Tasks

#### Task 3.1: Graph Data Model
**Time**: 1 hour
**Description**: Define graph structure for visualization

**Subtasks**:
- Define node structure (id, label, title, category, tags, size, color)
- Define edge structure (from, to, weight, title)
- Create `GraphData` dataclass
- Add validation for graph structure

**Deliverables**:
- Graph data models in `models.py`
- Validation functions

**Acceptance Criteria**:
- [ ] Node structure defined correctly
- [ ] Edge structure defined correctly
- [ ] Validation catches invalid structures

---

#### Task 3.2: Node Building Logic
**Time**: 2 hours
**Description**: Convert wiki notes to graph nodes

**Subtasks**:
- Implement `build_nodes() -> List[dict]`
- Load all wiki notes
- Extract node attributes from wiki notes
- Calculate node size based on link count
- Assign colors based on PARA category
- Generate labels from summaries

**Deliverables**:
- Node building function
- Size calculation logic
- Color assignment logic

**Acceptance Criteria**:
- [ ] All wiki notes converted to nodes
- [ ] Node sizes reflect centrality
- [ ] Colors match PARA categories
- [ ] Labels are readable

---

#### Task 3.3: Edge Building Logic
**Time**: 2 hours
**Description**: Convert wiki links to graph edges

**Subtasks**:
- Implement `build_edges() -> List[dict]`
- Load all wiki notes
- Extract links from each note
- Create edges between linked notes
- Add weights based on similarity scores
- Remove duplicate edges

**Deliverables**:
- Edge building function
- Weight assignment
- Deduplication logic

**Acceptance Criteria**:
- [ ] All links converted to edges
- [ ] Edge weights reflect similarity
- [ ] No duplicate edges
- [ ] Bidirectional links handled correctly

---

#### Task 3.4: Graph Export
**Time**: 1 hour
**Description**: Export graph data to JSON

**Subtasks**:
- Implement `export_graph(output_path: str) -> None`
- Combine nodes and edges
- Write to `graph.json`
- Add pretty-printing for readability
- Validate JSON structure

**Deliverables**:
- Graph export function
- `graph.json` output
- Validation

**Acceptance Criteria**:
- [ ] `graph.json` created with correct structure
- [ ] JSON is valid and readable
- [ ] Contains all nodes and edges
- [ ] Can be loaded by graph library

---

#### Task 3.5: Streamlit Graph Component Setup
**Time**: 2 hours
**Description**: Set up Streamlit with graph visualization library

**Subtasks**:
- Install `streamlit` and graph library (vis-network or Cytoscape)
- Create basic Streamlit app structure
- Implement custom component for graph rendering
- Load `graph.json` in app
- Render basic graph

**Deliverables**:
- Streamlit app skeleton
- Graph component
- Basic rendering

**Acceptance Criteria**:
- [ ] Streamlit app runs without errors
- [ ] Graph component loads
- [ ] `graph.json` loads successfully
- [ ] Basic graph renders

---

#### Task 3.6: Force-Directed Layout
**Time**: 2 hours
**Description**: Implement force-directed graph layout

**Subtasks**:
- Configure physics parameters (repulsion, spring length)
- Tune layout for readability
- Add node clustering by category
- Optimize for performance
- Test with different graph sizes

**Deliverables**:
- Layout configuration
- Physics parameters
- Performance tuning

**Acceptance Criteria**:
- [ ] Graph uses force-directed layout
- [ ] Nodes spread evenly
- [ ] Related nodes cluster together
- [ ] Layout renders quickly (< 3 seconds for 500 nodes)

---

#### Task 3.7: Interactive Features
**Time**: 3 hours
**Description**: Add interactive graph features

**Subtasks**:
- Implement hover tooltips with note content
- Add drag-and-drop node positioning
- Implement zoom and pan
- Add click-to-view-full-note
- Implement node selection

**Deliverables**:
- Hover tooltips
- Drag-and-drop
- Zoom/pan
- Click handlers

**Acceptance Criteria**:
- [ ] Hover shows note preview
- [ ] Nodes can be dragged
- [ ] Graph can be zoomed and panned
- [ ] Click opens note details
- [ ] Interactions are smooth

---

#### Task 3.8: Filtering and Search
**Time**: 2 hours
**Description**: Add graph filtering capabilities

**Subtasks**:
- Add filter by PARA category
- Add filter by tags
- Implement search by node label
- Add show/hide disconnected nodes
- Create filter UI in sidebar

**Deliverables**:
- Filter functions
- Search function
- Filter UI

**Acceptance Criteria**:
- [ ] Can filter by category
- [ ] Can filter by tags
- [ ] Search finds matching nodes
- [ ] UI is intuitive
- [ ] Filters update graph in real-time

---

#### Task 3.9: Visual Styling
**Time**: 2 hours
**Description**: Improve graph visual appearance

**Subtasks**:
- Design color scheme for PARA categories
- Style node borders and shadows
- Add edge styling (thickness by weight)
- Implement dark/light mode
- Add legend for categories

**Deliverables**:
- Color scheme
- Styling configuration
- Legend

**Acceptance Criteria**:
- [ ] Categories have distinct colors
- [ ] Visual hierarchy is clear
- [ ] Edge weights visible
- [ ] Dark/light mode works
- [ ] Legend is helpful

---

#### Task 3.10: Graph Auto-Update
**Time**: 2 hours
**Description**: Integrate graph building with capture pipeline

**Subtasks**:
- Trigger graph rebuild on new wiki notes
- Implement incremental graph updates
- Add auto-refresh in Streamlit
- Cache graph data for performance
- Handle large graphs gracefully

**Deliverables**:
- Auto-update logic
- Incremental updates
- Caching

**Acceptance Criteria**:
- [ ] Graph updates on new notes
- [ ] Updates are fast
- [ ] Streamlit refreshes automatically
- [ ] Large graphs don't crash app

---

#### Task 3.11: Testing with Real Data
**Time**: 3 hours
**Description**: Validate graph with real knowledge base

**Subtasks**:
- Build graph from Phase 2 wiki
- Verify all notes appear as nodes
- Verify all links appear as edges
- Test interactive features
- Check performance with real data
- Validate visual clustering

**Deliverables**:
- Graph built from real data
- Feature validation report
- Performance report

**Acceptance Criteria**:
- [ ] All wiki notes in graph
- [ ] All links represented
- [ ] Interactive features work
- [ ] Performance acceptable
- [ ] Visual clustering makes sense

---

### 3.2 Phase 3 Deliverables

**Primary Deliverable**: "Ship the Living Brain"
- Wiki converted to graph and rendered as interactive visual brain (hover, drag, zoom)
- Built from real notes, not dummy data
- 🏅 Badge: The Cartographer

### 3.3 Phase 3 Acceptance Criteria

- [ ] Script builds nodes + edges from notes and exports clean JSON
- [ ] Interactive force-directed graph renders from that JSON
- [ ] Hover reveals note content
- [ ] Drag + zoom work
- [ ] Built from real notes, not dummy data

### 3.4 Phase 3 Success Metrics

- **Functional**: All interactive features work smoothly
- **Visual**: Graph is readable and aesthetically pleasing
- **Performance**: Graph renders in < 3 seconds for 500 nodes
- **User Experience**: Intuitive navigation and exploration

---

## Phase 4: The Oracle — "Ask It Anything, Ship It Public"

**Duration**: Week 4
**Objective**: Implement RAG-based Q&A and deploy to public URL
**Badge**: The Oracle

### 4.1 Tasks

#### Task 4.1: Question Embedding
**Time**: 1 hour
**Description**: Implement embedding for user questions

**Subtasks**:
- Reuse embedding model from Phase 2
- Implement `embed_question(question: str) -> np.ndarray`
- Add question preprocessing
- Handle empty/invalid questions

**Deliverables**:
- Question embedding function
- Validation

**Acceptance Criteria**:
- [ ] Questions embedded correctly
- [ ] Same model as notes used
- [ ] Invalid questions handled

---

#### Task 4.2: Note Retrieval
**Time**: 2 hours
**Description**: Implement similarity search over wiki notes

**Subtasks**:
- Implement `retrieve_relevant_notes(question: str, top_k: int) -> List[dict]`
- Load all wiki embeddings
- Compute similarities with question embedding
- Sort by similarity score
- Return top-k notes with content and scores
- Add caching for repeated queries

**Deliverables**:
- Retrieval function
- Caching logic
- Scoring system

**Acceptance Criteria**:
- [ ] Returns most relevant notes
- [ ] Sorted by similarity
- [ ] Includes content and scores
- [ ] Configurable top-k
- [ ] Cache improves performance

---

#### Task 4.3: RAG Prompt Building
**Time**: 2 hours
**Description**: Construct context prompt for LLM

**Subtasks**:
- Implement `build_rag_prompt(question: str, notes: List[dict]) -> str`
- Format retrieved notes as context
- Add system instructions for answer synthesis
- Include citation requirements
- Handle context length limits

**Deliverables**:
- Prompt builder
- Context formatting
- Length management

**Acceptance Criteria**:
- [ ] Prompt includes relevant context
- [ ] Instructions are clear
- [ ] Citations required
- [ ] Context length managed

---

#### Task 4.4: Answer Synthesis
**Time**: 2 hours
**Description**: Generate answer using LLM with retrieved context

**Subtasks**:
- Implement `synthesize_answer(prompt: str) -> str`
- Call Groq API with RAG prompt
- Parse response for answer and citations
- Handle API errors gracefully
- Add fallback for failed synthesis

**Deliverables**:
- Synthesis function
- Response parser
- Error handling

**Acceptance Criteria**:
- [ ] Answer synthesized from context
- [ ] Citations included
- [ ] API errors handled
- [ ] Fallback mechanism works

---

#### Task 4.5: Ask Function Integration
**Time**: 2 hours
**Description**: Combine retrieval and synthesis into ask function

**Subtasks**:
- Implement `ask(question: str, top_k: int = 5) -> dict`
- Chain retrieval → prompt building → synthesis
- Return structured response with answer, sources, confidence
- Add logging
- Implement error recovery

**Deliverables**:
- Integrated `ask()` function
- Structured response format
- Logging

**Acceptance Criteria**:
- [ ] Returns answer with sources
- [ ] Confidence score included
- [ ] Errors logged
- [ ] Recovery works

---

#### Task 4.6: Streamlit Search UI
**Time**: 2 hours
**Description**: Build search interface in Streamlit

**Subtasks**:
-.Add search tab to Streamlit app
- Create question input field
- Add submit button
- Display answer with formatting
- Show source citations with links
- Add confidence indicator

**Deliverables**:
- Search UI components
- Answer display
- Source display

**Acceptance Criteria**:
- [ ] Question input works
- [ ] Answer displays clearly
- [ ] Sources shown with links
- [ ] Confidence visible
- [ ] UI is intuitive

---

#### Task 4.7: Unified App Integration
**Time**: 3 hours
**Description**: Combine graph and search in single Streamlit app

**Subtasks**:
- Integrate graph and search tabs
- Add sidebar with app navigation
- Implement shared state management
- Add capture interface to sidebar
- Ensure consistent styling
- Add app statistics

**Deliverables**:
- Unified Streamlit app
- Navigation
- Shared state
- Statistics

**Acceptance Criteria**:
- [ ] Graph and search in same app
- [ ] Navigation works smoothly
- [ ] State managed correctly
- [ ] Capture interface functional
- [ ] Styling consistent

---

#### Task 4.8: Real-Time Processing
**Time**: 2 hours
**Description**: Enable capture → classify → link → graph update in app

**Subtasks**:
- Integrate capture pipeline in app
- Trigger classification on capture
- Trigger linking on classification
- Trigger graph update on linking
- Add progress indicators
- Show processing status

**Deliverables**:
- Real-time pipeline
- Progress indicators
- Status display

**Acceptance Criteria**:
- [ ] Capture triggers full pipeline
- [ ] Progress shown to user
- [ ] Graph updates automatically
- [ ] Search includes new notes
- [ ] Status is clear

---

#### Task 4.9: App Configuration
**Time**: 1 hour
**Description**: Configure Streamlit app settings

**Subtasks**:
- Create `.streamlit/config.toml`
- Set theme colors
- Configure page settings
- Add app icon and title
- Set upload limits
- Configure logging

**Deliverables**:
- Streamlit config
- Theme settings
- App branding

**Acceptance Criteria**:
- [ ] Theme applied correctly
- [ ] Page title set
- [ ] Upload limits appropriate
- [ ] Logging configured

---

#### Task 4.10: Requirements Finalization
**Time**: 1 hour
**Description**: Finalize dependencies and versions

**Subtasks**:
- Update `requirements.txt` with all dependencies
- Pin versions for reproducibility
- Add development dependencies
- Test clean install
- Document dependency versions

**Deliverables**:
- Final `requirements.txt`
- Version documentation
- Install test

**Acceptance Criteria**:
- [ ] All dependencies listed
- [ ] Versions pinned
- [ ] Clean install works
- [ ] No conflicts

---

#### Task 4.11: GitHub Repository Setup
**Time**: 2 hours
**Description**: Prepare repository for deployment

**Subtasks**:
- Create GitHub repository
- Add comprehensive README
- Include setup instructions
- Add usage examples
- Configure `.gitignore`
- Add license file

**Deliverables**:
- GitHub repository
- README.md
- Setup documentation

**Acceptance Criteria**:
- [ ] Repository created
- [ ] README is comprehensive
- [ ] Setup instructions clear
- [ ] Examples provided
- [ ] License included

---

#### Task 4.12: Streamlit Cloud Deployment
**Time**: 2 hours
**Description**: Deploy app to Streamlit Cloud

**Subtasks**:
- Create Streamlit Cloud account
- Connect GitHub repository
- Configure environment variables
- Set deployment settings
- Test deployment
- Verify public URL

**Deliverables**:
- Deployed app
- Public URL
- Environment configuration

**Acceptance Criteria**:
- [ ] App deploys successfully
- [ ] Public URL accessible
- [ ] Environment variables set
- [ ] All features work in deployment
- [ ] No errors in deployment logs

---

#### Task 4.13: End-to-End Testing
**Time**: 3 hours
**Description**: Validate complete pipeline in deployed app

**Subtasks**:
- Test capture in deployed app
- Verify classification works
- Check linking functionality
- Validate graph updates
- Test search with real questions
- Verify all features end-to-end

**Deliverables**:
- E2E test report
- Bug fixes
- Performance validation

**Acceptance Criteria**:
- [ ] Capture works in deployment
- [ ] Classification accurate
- [ ] Linking functional
- [ ] Graph updates correctly
- [ ] Search returns relevant answers
- [ ] No critical bugs

---

#### Task 4.14: Documentation and Polish
**Time**: 2 hours
**Description**: Final documentation and UI polish

**Subtasks**:
- Add in-app help text
- Create user guide
- Add FAQ section
- Polish UI styling
- Add loading states
- Improve error messages

**Deliverables**:
- User guide
- Help text
- Polished UI

**Acceptance Criteria**:
- [ ] Help text clear
- [ ] User guide comprehensive
- [ ] UI looks professional
- [ ] Error messages helpful
- [ ] Loading states smooth

---

### 4.2 Phase 4 Deliverables

**Primary Deliverable**: "Ship SecondSelf"
- Complete system — capture → auto-classify → auto-link → live interactive graph → ask-anything search
- All wired into one Streamlit app with public URL
- 🏅 Badge: The Oracle

### 4.3 Phase 4 Acceptance Criteria

- [ ] `ask()` returns answers synthesized from own notes (retrieval + LLM)
- [ ] One Streamlit app contains both graph and search bar
- [ ] Deployed live with public URL
- [ ] Full pipeline works end to end in deployed app

### 4.4 Phase 4 Success Metrics

- **Functional**: Complete pipeline works in deployment
- **Quality**: Answers are relevant and well-sourced
- **Performance**: All operations < 5 seconds
- **User Experience**: Intuitive and responsive UI

---

## Final Deliverables (All Phases)

### Repository Structure
```
secondself/
├── raw/                          # Phase 1: Raw captures
├── wiki/                         # Phase 2: Processed notes
├── wiki/embeddings/              # Phase 2: Cached embeddings
├── graph.json                    # Phase 3: Graph data
├── cache/                        # Temporary cache
├── config/                       # Configuration files
│   ├── prompts.json             # LLM prompts
│   └── thresholds.json          # Similarity thresholds
├── .streamlit/                   # Phase 4: Streamlit config
│   └── config.toml
├── capture.py                    # Phase 1: Capture module
├── classify.py                   # Phase 2: Classification module
├── link.py                       # Phase 2: Linking module
├── build_graph.py                # Phase 3: Graph building
├── ask.py                        # Phase 4: Query module
├── app.py                        # Phase 4: Streamlit app
├── utils.py                      # Helper functions
├── models.py                     # Data models
├── llm_client.py                 # LLM API client
├── embeddings.py                 # Embedding utilities
├── requirements.txt              # Dependencies
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── README.md                     # Documentation
├── ARCHITECTURE.md               # Architecture document
├── IMPLEMENTATION_PLAN.md        # This file
└── LICENSE                       # License file
```

### GitHub Repository Requirements
- [ ] Public GitHub repository with clean README
- [ ] Setup instructions for local development
- [ ] Usage examples and screenshots
- [ ] Architecture documentation linked
- [ ] License file (MIT recommended)
- [ ] Contributing guidelines (optional)

### Deployment Requirements
- [ ] Live deployed URL (Streamlit Cloud or HF Spaces)
- [ ] Interactive graph renders correctly
- [ ] Ask-your-brain search works
- [ ] Full pipeline functional in deployment
- [ ] Environment variables configured
- [ ] No critical errors in logs

### End-to-End Verification
- [ ] Capture → classify → link → graph → ask pipeline works
- [ ] All 4 weekly milestones complete
- [ ] Tested with real personal data (not dummy data)
- [ ] Performance meets targets (< 5 seconds per operation)
- [ ] UI is intuitive and responsive
- [ ] Code is clean and documented

---

## Risk Management

### Technical Risks

#### Risk 1: Groq API Rate Limits or Downtime
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Implement exponential backoff for retries
- Cache LLM responses for similar inputs
- Have fallback to local models (Ollama) if needed
- Queue requests to stay within rate limits

#### Risk 2: Embedding Model Performance
**Probability**: Low
**Impact**: Medium
**Mitigation**:
- Use established model (all-MiniLM-L6-v2)
- Benchmark alternatives during Phase 2
- Cache embeddings to avoid recomputation
- Monitor similarity quality during testing

#### Risk 3: Graph Rendering Performance
**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- Implement pagination for large graphs
- Use WebGL acceleration
- Lazy load graph data
- Limit initial node count
- Test with progressively larger datasets

#### Risk 4: Deployment Platform Limitations
**Probability**: Low
**Impact**: High
**Mitigation**:
- Have backup deployment options (HF Spaces, Railway)
- Test deployment early in Phase 4
- Monitor resource usage during development
- Optimize for free tier constraints

### Project Risks

#### Risk 5: Scope Creep in Phase 4
**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- Keep UI simple and functional
- Prioritize core features over polish
- Defer advanced features to future iterations
- Timebox each task strictly

#### Risk 6: Data Loss During Development
**Probability**: Low
**Impact**: High
**Mitigation**:
- Regular git commits
- Backup `raw/` and `wiki/` directories
- Use git for code versioning
- Test destructive operations on copies first

#### Risk 7: Insufficient Real Data for Testing
**Probability**: Low
**Impact**: Medium
**Mitigation**:
- Start data collection early (Phase 1)
- Use personal bookmarks, notes, files
- Generate synthetic data only if necessary
- Document data sources for reproducibility

---

## Time Management

### Weekly Time Allocation

**Phase 1 (Week 1)**: ~20 hours
- Project setup: 3 hours
- Core capture functionality: 10 hours
- Testing with real data: 4 hours
- Documentation and polish: 3 hours

**Phase 2 (Week 2)**: ~25 hours
- LLM integration: 4 hours
- Classification pipeline: 8 hours
- Embedding and linking: 8 hours
- Testing and validation: 5 hours

**Phase 3 (Week 3)**: ~20 hours
- Graph building: 6 hours
- Visualization implementation: 10 hours
- Testing and refinement: 4 hours

**Phase 4 (Week 4)**: ~25 hours
- RAG implementation: 8 hours
- Streamlit integration: 10 hours
- Deployment and testing: 7 hours

**Total**: ~90 hours over 4 weeks

### Milestone Checkpoints

**End of Week 1**: Capture pipeline complete
- [ ] 10+ real items captured
- [ ] All capture types working
- [ ] Ready for Phase 2

**End of Week 2**: Organization pipeline complete
- [ ] 15+ items classified and linked
- [ ] Wiki structure validated
- [ ] Ready for Phase 3

**End of Week 3**: Visualization complete
- [ ] Interactive graph working
- [ ] All features functional
- [ ] Ready for Phase 4

**End of Week 4**: Full system deployed
- [ ] Public URL live
- [ ] All features working end-to-end
- [ ] Documentation complete

---

## Quality Assurance

### Code Quality Standards
- **PEP 8 compliance**: All Python code follows style guide
- **Type hints**: All functions have type annotations
- **Docstrings**: All public functions documented
- **Black formatting**: Code formatted with Black
- **Unit tests**: Critical functions have tests
- **Error handling**: All functions handle errors gracefully

### Testing Strategy
- **Unit tests**: For individual functions (utils, models, embeddings)
- **Integration tests**: For pipeline components (capture → classify → link)
- **Manual tests**: With real data each phase
- **E2E tests**: Complete pipeline in deployed app

### Validation Criteria
- **Phase 1**: 10+ real captures, zero data loss
- **Phase 2**: 15+ items processed, reasonable classifications
- **Phase 3**: Graph renders, all features work
- **Phase 4**: Deployment functional, search returns relevant answers

---

## Success Metrics

### Functional Metrics
- **Capture**: Supports notes, links, files with single command
- **Classification**: PARA accuracy > 80% (manual check)
- **Linking**: Semantic links make sense
- **Graph**: Interactive, responsive, visually clear
- **Search**: Relevant answers with proper citations
- **Deployment**: Public URL accessible, all features work

### Performance Metrics
- **Capture**: < 1 second local, < 3 seconds with classification
- **Classification**: < 5 seconds per note
- **Linking**: < 2 seconds per note (cached)
- **Graph render**: < 3 seconds for 500 nodes
- **Search**: < 5 seconds (retrieval + synthesis)

### User Experience Metrics
- **Learnability**: Can capture in < 1 minute
- **Efficiency**: Can find information in < 30 seconds
- **Satisfaction**: Graph exploration is intuitive
- **Reliability**: No crashes in normal usage

---

## Post-Launch Considerations

### Future Enhancements (Backlog)
- Multi-modal support (images, audio)
- Advanced graph layouts (hierarchical, temporal)
- Collaboration features (share brains)
- Mobile app (iOS/Android)
- Browser extension (one-click capture)
- Advanced RAG (hybrid search)
- Knowledge extraction (insights, summaries)
- Backup/sync (cloud storage)

### Maintenance Tasks
- Monitor API usage and costs
- Update dependencies regularly
- Fix bugs reported by users
- Optimize performance based on usage
- Add features based on feedback

### Scaling Considerations
- Move to database if filesystem becomes limiting
- Implement vector database for embeddings
- Add caching layer (Redis)
- Implement API server (FastAPI)
- Add authentication for private deployments

---

## Conclusion

This implementation plan provides a structured, phase-wise approach to building SecondSelf. Each phase builds on the previous one, ensuring incremental progress and continuous validation with real data.

**Key Success Factors**:
1. **Real data testing**: Each phase validated with actual personal knowledge
2. **Incremental delivery**: Working software at each phase end
3. **Quality focus**: Testing, error handling, and code quality
4. **User-centric**: Intuitive UI and smooth user experience
5. **Deployment-ready**: Public URL by end of Phase 4

Following this plan will result in a fully functional, deployed AI second brain that captures, organizes, visualizes, and queries personal knowledge effectively.

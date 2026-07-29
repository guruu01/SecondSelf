# 🧠 SecondSelf - Personal AI Second Brain

An AI-powered personal knowledge management system that captures, organizes, visualizes, and queries your notes automatically.

## ✨ Features

- **📝 Universal Capture**: Capture notes, links, and files with a single command
- **🏷️ PARA Auto-Classification**: AI automatically categorizes notes into Projects, Areas, Resources, or Archives
- **🔗 Semantic Auto-Linking**: Automatically links related notes based on content similarity
- **📊 Interactive Knowledge Graph**: Visualize your knowledge as an interactive force-directed graph
- **🔍 Ask-Anything Search**: Query your knowledge base with natural language using RAG
- **⚡ Real-Time Processing**: Capture → Classify → Link → Graph update in one flow

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Groq API key (free at [groq.com](https://groq.com))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SecondSelf.git
cd SecondSelf
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Running the App

Start the Streamlit app:
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📖 Usage

### Capturing Content

**Via the App:**
1. Open the sidebar in the Knowledge Graph tab
2. Expand "Add new note"
3. Type your note and click "✨ Capture & Process"

**Via CLI:**
```bash
# Capture a note
python -m capture "Your note content here"

# Capture a link
python -m capture "https://example.com" --type link

# Capture a file
python -m capture "/path/to/file.txt" --type file
```

### Processing Captures

Process raw captures into wiki notes:
```bash
# Single capture
python process.py <raw_id>

# Batch process
python process.py --batch <raw_id1>,<raw_id2>,...
```

### Building the Knowledge Graph

The graph is automatically built when you capture notes through the app. To rebuild manually:

```bash
python graph.py
```

### Exporting to Obsidian

Export your wiki notes to Obsidian-compatible markdown:
```bash
python export_obsidian.py
```

This creates an `obsidian_vault/` directory ready for import.

## 🏗️ Architecture

```
SecondSelf/
├── raw/                    # Raw captures (Phase 1)
├── wiki/                   # Processed wiki notes (Phase 2)
│   └── embeddings/         # Cached embeddings
├── graph.json              # Knowledge graph data (Phase 3)
├── config/                 # Configuration files
├── capture.py              # Capture module
├── classify.py             # PARA classification
├── wiki.py                 # Wiki note management
├── linking.py              # Auto-linking logic
├── embeddings.py           # Embedding computation
├── graph.py                # Graph building
├── ask.py                  # RAG-based Q&A (Phase 4)
├── app.py                  # Streamlit application
├── models.py               # Data models
├── llm_client.py           # Groq API client
└── utils.py                # Helper functions
```

## 🎯 PARA Framework

The system uses the [PARA method](https://fortelabs.co/para/) for organization:

- **Projects**: Short-term efforts with specific goals
- **Areas**: Ongoing responsibilities with no completion date
- **Resources**: Topics of ongoing interest
- **Archives**: Completed or inactive items

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### Similarity Threshold

Adjust the auto-linking threshold in `config/thresholds.json`:

```json
{
  "link_threshold": 0.75
}
```

Higher values = stricter linking, lower values = more connections.

## 📊 Knowledge Graph Features

- **Force-directed layout** with Barnes-Hut physics
- **Interactive**: Drag nodes, zoom, pan
- **Hover tooltips** with note previews
- **Category filtering** by PARA type
- **Search** by content, tags, or title
- **Color-coded** by category:
  - Projects: Red (#FF6B6B)
  - Areas: Teal (#4ECDC4)
  - Resources: Blue (#45B7D1)
  - Archives: Green (#96CEB4)

## 🔍 Ask Your Brain

The "Ask Your Brain" tab uses RAG (Retrieval-Augmented Generation) to answer questions:

1. Enter your question in natural language
2. System retrieves semantically similar notes
3. LLM synthesizes an answer with citations
4. View confidence scores and source notes

## 🧪 Testing

Run unit tests:
```bash
pytest tests/
```

## 📝 Development

### Code Style

```bash
# Format code with Black
black .

# Run type checking (optional)
mypy .
```

### Adding New Features

1. Create a feature branch
2. Make changes with tests
3. Run tests and format code
4. Submit a pull request

## 🚀 Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add `GROQ_API_KEY` in secrets
5. Deploy!

### Local Production

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Groq](https://groq.com) for fast LLM inference
- [sentence-transformers](https://www.sbert.net/) for semantic embeddings
- [Streamlit](https://streamlit.io/) for the web framework
- [pyvis](https://pyvis.readthedocs.io/) for graph visualization
- [PARA Method](https://fortelabs.co/para/) by Tiago Forte

## 🐛 Troubleshooting

**Issue**: "GROQ_API_KEY not found"
- **Solution**: Ensure `.env` file exists and contains your API key

**Issue**: Graph rendering slowly
- **Solution**: Reduce node count with filters or increase similarity threshold

**Issue**: Classification inaccurate
- **Solution**: Check prompts in `config/prompts.json` and adjust few-shot examples

**Issue**: Embedding model not downloading
- **Solution**: Ensure internet connection and sufficient disk space (~500MB)

## 📈 Roadmap

- [ ] Multi-modal support (images, audio)
- [ ] Mobile app (iOS/Android)
- [ ] Browser extension for one-click capture
- [ ] Advanced RAG with hybrid search
- [ ] Collaboration features
- [ ] Cloud sync and backup

## 📧 Contact

For questions or feedback, open an issue on GitHub.

---

Built with ❤️ for personal knowledge management

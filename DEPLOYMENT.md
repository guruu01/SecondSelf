# Deployment Guide

## Streamlit Cloud Deployment

### Prerequisites

1. GitHub account with the repository pushed
2. Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))
3. Groq API key

### Step-by-Step Deployment

#### 1. Push to GitHub

```bash
git add .
git commit -m "Phase 4 complete: RAG-based Q&A and unified app"
git push origin main
```

#### 2. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Select the repository: `SecondSelf`
5. Select the branch: `main`
6. Main file path: `app.py`
7. Click "Deploy"

#### 3. Configure Environment Variables

In your Streamlit Cloud app settings:

1. Go to "Settings" → "Secrets"
2. Add the following secret:
   ```
   GROQ_API_KEY=your_actual_api_key_here
   ```
3. Save and redeploy

#### 4. Verify Deployment

- The app should be accessible at: `https://your-app-name.streamlit.app`
- Test both tabs (Knowledge Graph and Ask Your Brain)
- Test the quick capture feature

### Troubleshooting Deployment

**Issue**: App fails to start
- **Solution**: Check logs in Streamlit Cloud dashboard for errors

**Issue**: GROQ_API_KEY errors
- **Solution**: Ensure the secret is set correctly in app settings

**Issue**: Model download fails
- **Solution**: The first run may take longer as it downloads the embedding model (~500MB)

**Issue**: Graph doesn't render
- **Solution**: Ensure `graph.json` exists or the app can build it from wiki notes

### Alternative Deployment Options

#### Hugging Face Spaces

```bash
# Create a Space on huggingface.co
# Upload your files
# Add requirements.txt
# Set up app.py as the main file
```

#### Railway/Render

1. Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. Deploy using Railway/Render CLI

### Local Production Deployment

For running locally in production mode:

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Performance Optimization

For larger knowledge bases (>1000 notes):

1. Use a vector database (e.g., Pinecone, Weaviate)
2. Implement caching for embeddings
3. Add pagination for graph visualization
4. Use lazy loading for graph nodes

### Security Considerations

- Never commit `.env` file to version control
- Use environment variables for all secrets
- Enable authentication for private deployments
- Regularly update dependencies
- Monitor API usage and costs

### Monitoring

Streamlit Cloud provides:
- Resource usage metrics
- Error logs
- Deployment history
- User analytics (for paid plans)

### Backup Strategy

- Regularly backup `raw/`, `wiki/`, and `graph.json`
- Use git for code versioning
- Consider cloud storage for knowledge base data
- Export to Obsidian periodically as backup

"""
Streamlit app for interactive knowledge graph visualization and search.
"""
import streamlit as st
import json
from pathlib import Path
from graph import build_graph, CATEGORY_COLORS
from models import GraphData
from ask import ask
from capture import capture_note
from process import process_capture


st.set_page_config(
    page_title="SecondSelf - Knowledge Graph",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_graph_data() -> GraphData:
    """
    Load or build graph data.
    
    Returns:
        GraphData object.
    """
    # Try to load from cached file
    graph_file = Path("graph.json")
    if graph_file.exists():
        with open(graph_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return GraphData(
                nodes=[GraphNode(**node) for node in data["nodes"]],
                edges=[
                    GraphEdge(
                        from_=edge["from"],
                        to=edge["to"],
                        weight=edge.get("weight", 0.0),
                        title=edge.get("title", "")
                    )
                    for edge in data["edges"]
                ]
            )
    
    # Build fresh graph
    return build_graph()


def render_graph(graph_data: GraphData):
    """
    Render interactive graph using pyvis.
    
    Args:
        graph_data: GraphData object with nodes and edges.
    """
    from pyvis.network import Network
    import tempfile
    
    # Create network
    net = Network(
        height="700px",
        width="100%",
        bgcolor="#1e1e1e",
        font_color="#ffffff",
        directed=False
    )
    
    # Configure physics for force-directed layout
    net.set_options("""
    {
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -8000,
          "centralGravity": 0.3,
          "springLength": 200,
          "springConstant": 0.04,
          "damping": 0.09,
          "avoidOverlap": 0.5
        },
        "maxVelocity": 50,
        "minVelocity": 0.1,
        "solver": "barnesHut",
        "timestep": 0.5,
        "stabilization": {
          "enabled": true,
          "iterations": 1000,
          "updateInterval": 50,
          "onlyDynamicEdges": false,
          "fit": true
        }
      },
      "nodes": {
        "borderWidth": 2,
        "borderWidthSelected": 3,
        "font": {
          "size": 14,
          "color": "#ffffff"
        },
        "shadow": {
          "enabled": true,
          "color": "rgba(0,0,0,0.3)",
          "size": 10,
          "x": 5,
          "y": 5
        }
      },
      "edges": {
        "width": 2,
        "smooth": {
          "type": "continuous",
          "forceDirection": "none",
          "roundness": 0.5
        },
        "color": {
          "color": "#888888",
          "highlight": "#ffffff",
          "hover": "#aaaaaa"
        }
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 200,
        "zoomView": true,
        "dragView": true
      }
    }
    """)
    
    # Add nodes
    for node in graph_data.nodes:
        net.add_node(
            node.id,
            label=node.label,
            title=f"{node.title}\n\nCategory: {node.category}\nTags: {', '.join(node.tags)}\n\n{node.content[:200]}...",
            color=node.color,
            size=node.size,
            shape="dot"
        )
    
    # Add edges
    for edge in graph_data.edges:
        net.add_edge(
            edge.from_,
            edge.to,
            title=edge.title,
            value=edge.weight * 5,  # Scale edge width by weight
            width=edge.weight * 5
        )
    
    # Save to temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        temp_path = f.name
        net.save_graph(temp_path)
    
    # Read and display
    with open(temp_path, 'r', encoding='utf-8') as f:
        html_string = f.read()
    
    st.components.v1.html(html_string, height=700, scrolling=False)


def render_search_tab():
    """Render the search/ask tab."""
    st.header("🔍 Ask Your Knowledge Base")
    st.markdown("Ask anything and get answers synthesized from your personal notes.")
    
    # Search input
    question = st.text_area(
        "Enter your question:",
        placeholder="e.g., What are the key components of this project?",
        height=100
    )
    
    # Top-k selector
    top_k = st.slider("Number of notes to retrieve", min_value=1, max_value=10, value=5)
    
    # Ask button
    if st.button("🚀 Ask", type="primary") and question:
        with st.spinner("Searching your knowledge base..."):
            try:
                result = ask(question, top_k)
                
                # Display answer
                st.subheader("Answer")
                st.markdown(result["answer"])
                
                # Display confidence
                confidence = result["confidence"]
                st.metric("Confidence Score", f"{confidence:.2f}")
                
                # Display sources
                if result["sources"]:
                    st.subheader("Sources")
                    for i, source in enumerate(result["sources"], 1):
                        with st.expander(f"Source {i}: {source['summary']} (Relevance: {source['score']:.2f})"):
                            st.write(f"**Category:** {source['category']}")
                            st.write(f"**Note ID:** {source['id']}")
                            st.write(f"**Relevance Score:** {source['score']:.2f}")
                else:
                    st.info("No sources found.")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Help text
    with st.expander("💡 Tips for better results"):
        st.markdown("""
        - Be specific in your questions
        - Use keywords that appear in your notes
        - Ask about topics you've captured
        - The system uses semantic similarity, so related concepts work well
        """)


def main():
    """Main Streamlit app."""
    st.title("🧠 SecondSelf - Personal AI Second Brain")
    st.markdown("""
    Welcome to your AI-powered personal knowledge management system. 
    
    **Features:**
    - 📊 **Knowledge Graph**: Visualize your notes as an interactive network
    - 🔍 **Ask Your Brain**: Query your knowledge with natural language
    - ✨ **Quick Capture**: Add notes that auto-classify and auto-link
    
    **Getting Started:**
    1. Use the sidebar to capture new notes
    2. Watch them appear in the Knowledge Graph
    3. Ask questions in the "Ask Your Brain" tab
    """)
    
    # Create tabs
    tab1, tab2 = st.tabs(["📊 Knowledge Graph", "🔍 Ask Your Brain"])
    
    with tab1:
        st.markdown("### Interactive visualization of your personal knowledge base")
        render_graph_tab()
    
    with tab2:
        render_search_tab()


def render_graph_tab():
    """Render the graph visualization tab."""
    # Sidebar
    st.sidebar.header("📝 Quick Capture")
    
    # Quick capture interface
    with st.sidebar.expander("Add new note", expanded=False):
        new_note = st.text_area(
            "Enter your note:",
            placeholder="Type something to capture...",
            height=100
        )
        if st.button("✨ Capture & Process", key="capture_btn"):
            if new_note and new_note.strip():
                with st.spinner("Capturing and processing..."):
                    try:
                        # Step 1: Capture
                        raw_id = capture_note(new_note.strip())
                        st.success(f"✓ Captured: {raw_id[:8]}...")
                        
                        # Step 2: Process (classify → wiki → link)
                        wiki_id = process_capture(raw_id, link_threshold=0.75)
                        st.success(f"✓ Processed: {wiki_id[:8]}...")
                        
                        # Step 3: Rebuild graph
                        from graph import export_graph
                        export_graph()
                        st.success("✓ Graph updated")
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a note")
    
    st.sidebar.header("Graph Controls")
    
    # Load graph data
    with st.spinner("Loading graph data..."):
        graph_data = load_graph_data()
    
    # Display statistics
    st.sidebar.subheader("Statistics")
    st.sidebar.metric("Total Notes", len(graph_data.nodes))
    st.sidebar.metric("Total Links", len(graph_data.edges))
    
    # Category distribution
    st.sidebar.subheader("Category Distribution")
    category_counts = {}
    for node in graph_data.nodes:
        category_counts[node.category] = category_counts.get(node.category, 0) + 1
    
    for category, count in category_counts.items():
        color = CATEGORY_COLORS.get(category, "#97C2FC")
        st.sidebar.markdown(
            f"<span style='color:{color}; font-weight:bold;'>●</span> {category}: {count}",
            unsafe_allow_html=True
        )
    
    # Filter by category
    st.sidebar.subheader("Filter by Category")
    selected_categories = st.sidebar.multiselect(
        "Select categories to display",
        options=list(CATEGORY_COLORS.keys()),
        default=list(CATEGORY_COLORS.keys())
    )
    
    # Filter nodes by category
    if selected_categories:
        filtered_node_ids = {node.id for node in graph_data.nodes if node.category in selected_categories}
        filtered_nodes = [node for node in graph_data.nodes if node.category in selected_categories]
        filtered_edges = [edge for edge in graph_data.edges 
                         if edge.from_ in filtered_node_ids and edge.to in filtered_node_ids]
        graph_data = GraphData(nodes=filtered_nodes, edges=filtered_edges)
    
    # Search functionality
    st.sidebar.subheader("Search")
    search_query = st.sidebar.text_input("Search notes...")
    
    if search_query:
        query_lower = search_query.lower()
        filtered_node_ids = set()
        filtered_nodes = []
        
        for node in graph_data.nodes:
            if (query_lower in node.label.lower() or 
                query_lower in node.title.lower() or 
                query_lower in node.content.lower() or
                any(query_lower in tag.lower() for tag in node.tags)):
                filtered_node_ids.add(node.id)
                filtered_nodes.append(node)
        
        filtered_edges = [edge for edge in graph_data.edges 
                         if edge.from_ in filtered_node_ids and edge.to in filtered_node_ids]
        graph_data = GraphData(nodes=filtered_nodes, edges=filtered_edges)
    
    # Show/hide disconnected nodes
    show_disconnected = st.sidebar.checkbox("Show disconnected nodes", value=True)
    
    if not show_disconnected:
        connected_node_ids = set()
        for edge in graph_data.edges:
            connected_node_ids.add(edge.from_)
            connected_node_ids.add(edge.to)
        
        filtered_nodes = [node for node in graph_data.nodes if node.id in connected_node_ids]
        graph_data = GraphData(nodes=filtered_nodes, edges=graph_data.edges)
    
    # Rebuild button
    if st.sidebar.button("🔄 Rebuild Graph"):
        from graph import export_graph
        export_graph()
        st.rerun()
    
    # Render graph
    if graph_data.nodes:
        render_graph(graph_data)
    else:
        st.warning("No nodes to display. Try adjusting your filters.")


if __name__ == "__main__":
    # Import models for type hints
    from models import GraphNode, GraphEdge
    main()

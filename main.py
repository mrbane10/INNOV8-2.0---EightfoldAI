"""
HR Fraud Detection Dashboard
Simple, focused interface for fraud analysis
"""

import streamlit as st
import networkx as nx
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import json
import csv
import pickle
from pathlib import Path
from typing import Dict, List
import warnings

warnings.filterwarnings('ignore')

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    layout="wide",
    page_title="HR Fraud Detection",
    page_icon="🔍",
    initial_sidebar_state="collapsed"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    /* Clean, professional styling */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .main {
        padding: 1rem 2rem;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    
    /* Fraud score card */
    .fraud-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 6px solid #ef4444;
        margin: 1rem 0;
    }
    
    .fraud-card.safe {
        border-left-color: #10b981;
    }
    
    .fraud-score {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
    }
    
    .fraud-score.high {
        color: #ef4444;
    }
    
    .fraud-score.medium {
        color: #f59e0b;
    }
    
    .fraud-score.low {
        color: #10b981;
    }
    
    /* Section styling */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    /* User list styling */
    .user-badge {
        display: inline-block;
        background: #f1f5f9;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 0.25rem;
        font-weight: 500;
    }
    
    /* Button styling */
    .stButton > button {
        background: #3b82f6;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: #2563eb;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATA LOADING ====================

@st.cache_data
def load_csv_data(file_path: str) -> pd.DataFrame:
    """Load CSV data."""
    try:
        return pd.read_csv(file_path)
    except:
        return pd.DataFrame()

@st.cache_data
def load_endorsement_data(csv_path: str) -> Dict[str, List[str]]:
    """Load endorsement data."""
    endorsement_data = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                if len(row) >= 2:
                    user_id, recommenders = row[0], row[1]
                    try:
                        endorsement_data[user_id] = json.loads(recommenders.replace("'", '"'))
                    except:
                        try:
                            endorsement_data[user_id] = eval(recommenders)
                        except:
                            pass
    except:
        pass
    return endorsement_data

@st.cache_resource
def load_or_create_graph(pickle_path: str, endorsement_data: Dict[str, List[str]]) -> nx.DiGraph:
    """Load or create graph."""
    if Path(pickle_path).exists():
        try:
            with open(pickle_path, "rb") as f:
                return pickle.load(f)
        except:
            pass
    
    G = nx.DiGraph()
    all_nodes = set(endorsement_data.keys())
    for recommenders in endorsement_data.values():
        all_nodes.update(str(r) for r in recommenders)
    
    for node in all_nodes:
        G.add_node(str(node))
    
    for user_id, recommender_ids in endorsement_data.items():
        for recommender_id in recommender_ids:
            G.add_edge(str(recommender_id), str(user_id))
    
    try:
        with open(pickle_path, "wb") as f:
            pickle.dump(G, f)
    except:
        pass
    
    return G

@st.cache_resource
def build_endorsement_graph(endorsement_data: Dict[str, List[str]]) -> nx.DiGraph:
    """Build endorsement graph."""
    G = nx.DiGraph()
    all_nodes = set(endorsement_data.keys())
    for recommenders in endorsement_data.values():
        all_nodes.update(str(r) for r in recommenders)
    
    for node in all_nodes:
        G.add_node(str(node))
    
    for user_id, recommender_ids in endorsement_data.items():
        for recommender_id in recommender_ids:
            G.add_edge(str(recommender_id), str(user_id))
    
    return G

def calculate_node_similarity(G: nx.DiGraph, node1: str, node2: str) -> float:
    """Calculate Jaccard similarity."""
    try:
        preds1 = set(G.predecessors(node1))
        preds2 = set(G.predecessors(node2))
        intersection = preds1 & preds2
        union = preds1 | preds2
        return len(intersection) / len(union) if len(union) > 0 else 0.0
    except:
        return 0.0

def visualize_graph(G: nx.DiGraph, highlight_node: str = None) -> str:
    """Create network visualization."""
    net = Network(height="600px", width="100%", notebook=False, directed=True,
                  bgcolor="#ffffff", font_color="#000000", cdn_resources='in_line')
    
    net.barnes_hut(gravity=-80000, central_gravity=0.3, spring_length=100,
                   spring_strength=0.001, damping=0.9)
    
    try:
        pagerank = nx.pagerank(G, max_iter=100)
    except:
        pagerank = {node: 1.0 for node in G.nodes}
    
    for node in G.nodes:
        node_size = pagerank.get(node, 0) * 200 + 10
        color = "#ef4444" if node == highlight_node else "#3b82f6"
        net.add_node(node, size=node_size, color=color,
                    title=f"User: {node}")
    
    for edge in G.edges:
        net.add_edge(edge[0], edge[1])
    
    net.set_options("""
    {
      "nodes": {"scaling": {"min": 10, "max": 30}},
      "edges": {"color": {"inherit": true}, "smooth": {"type": "continuous"}},
      "physics": {
        "barnesHut": {"gravitationalConstant": -80000, "springLength": 100,
                      "springConstant": 0.001, "damping": 0.9},
        "minVelocity": 0.75
      },
      "interaction": {"hover": true}
    }
    """)
    
    output_path = "graph_visualization.html"
    net.save_graph(output_path)
    return output_path

# ==================== MAIN APPLICATION ====================

def main():
    # Header
    st.markdown('<h1 class="main-header">🔍 HR Fraud Detection Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Analyze candidate profiles and detect potential fraud</p>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading data..."):
        df = load_csv_data("/Users/kaisarimtiyaz/Desktop/Competitions/INNOV8-2.0/out-data/output.csv")
        fraud_df = load_csv_data("/Users/kaisarimtiyaz/Desktop/Competitions/ariesiitd/finals/INNOV8-2.0-Finals/final_df.csv")
        endorsement_data = load_endorsement_data("/Users/kaisarimtiyaz/Desktop/Competitions/ariesiitd/finals/INNOV8-2.0-Finals/Dataset/Final_Persons_And_Recommenders.csv")
        
        if not endorsement_data:
            st.error("Cannot load data. Please check file paths.")
            st.stop()
        
        G = load_or_create_graph("graph.pickle", endorsement_data)
        G2 = build_endorsement_graph(endorsement_data)
    
    user_ids = sorted([str(node) for node in G.nodes()])
    
    # ==================== USER SELECTION ====================
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_user = st.selectbox(
            "**Select Candidate to Review**",
            user_ids,
            help="Choose a candidate ID to view their fraud analysis"
        )
    with col2:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh Analysis", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # ==================== FRAUD SCORE SECTION ====================
    st.markdown('<div class="section-header">🚨 Fraud Risk Assessment</div>', unsafe_allow_html=True)
    
    # Get fraud data
    fraud_score = None
    fraud_flag = False
    
    if not fraud_df.empty:
        if 'ID' in fraud_df.columns:
            fraud_row = fraud_df[fraud_df['ID'].astype(str) == selected_user]
        else:
            try:
                fraud_row = fraud_df.iloc[[int(selected_user)]]
            except:
                fraud_row = pd.DataFrame()
        
        if not fraud_row.empty:
            fraud_idx = fraud_row.index[0]
            if 'fraud_score' in fraud_df.columns:
                fraud_score = fraud_df['fraud_score'].iloc[fraud_idx]
            if 'fraud' in fraud_df.columns:
                fraud_flag = bool(fraud_df['fraud'].iloc[fraud_idx])
    
    # Display fraud score
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if fraud_score is not None:
            score_class = "high" if fraud_score > 0.7 else "medium" if fraud_score > 0.4 else "low"
            card_class = "" if fraud_score > 0.5 else "safe"
            
            st.markdown(f"""
            <div class="fraud-card {card_class}">
                <h3 style="margin: 0; color: #64748b;">Fraud Score</h3>
                <p class="fraud-score {score_class}">{fraud_score:.2%}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Fraud score not available")
    
    with col2:
        if fraud_flag:
            st.markdown("""
            <div class="fraud-card">
                <h3 style="margin: 0; color: #64748b;">Status</h3>
                <p style="font-size: 1.5rem; font-weight: 700; color: #ef4444; margin: 0.5rem 0;">
                    ⚠️ FLAGGED
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="fraud-card safe">
                <h3 style="margin: 0; color: #64748b;">Status</h3>
                <p style="font-size: 1.5rem; font-weight: 700; color: #10b981; margin: 0.5rem 0;">
                    ✓ VERIFIED
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        endorsements_received = G2.in_degree(selected_user) if G2.has_node(selected_user) else 0
        st.markdown(f"""
        <div class="fraud-card safe">
            <h3 style="margin: 0; color: #64748b;">Endorsements</h3>
            <p style="font-size: 2rem; font-weight: 700; color: #3b82f6; margin: 0.5rem 0;">
                {endorsements_received}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Additional scores if available
    if not df.empty:
        user_row = df[df['ID'].astype(str) == selected_user]
        if not user_row.empty:
            user_idx = user_row.index[0]
            
            st.markdown("**Detailed Scores:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'Resume Score based on Recommendations' in df.columns:
                    score = df['Resume Score based on Recommendations'].iloc[user_idx]
                    st.metric("Recommendation Score", f"{score:.2f}")
            
            with col2:
                if 'Suspicious Wording Score' in df.columns:
                    score = df['Suspicious Wording Score'].iloc[user_idx]
                    st.metric("Suspicious Wording", f"{score:.2f}")
            
            with col3:
                if 'Recommendation Redundancy Score' in df.columns:
                    score = df['Recommendation Redundancy Score'].iloc[user_idx]
                    st.metric("Redundancy Score", f"{score:.2f}")
    
    # ==================== NETWORK GRAPH ====================
    st.markdown('<div class="section-header">🕸️ Network Visualization</div>', unsafe_allow_html=True)
    st.markdown(f"**Viewing network connections for User {selected_user}** (highlighted in red)")
    
    with st.spinner("Rendering network..."):
        graph_html_path = visualize_graph(G, highlight_node=selected_user)
        with open(graph_html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        components.html(html_content, height=650, scrolling=True)
    
    # ==================== COMPARISON SECTION ====================
    st.markdown('<div class="section-header">🔗 Compare with Another Candidate</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        compare_user = st.selectbox(
            "Select candidate to compare",
            [uid for uid in user_ids if uid != selected_user],
            key="compare_user"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("Calculate Similarity", use_container_width=True):
            similarity = calculate_node_similarity(G, selected_user, compare_user)
            
            st.markdown("---")
            st.markdown("### Similarity Analysis")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                st.metric("User A", selected_user)
            with col2:
                st.markdown(f"""
                <div style="text-align: center;">
                    <h1 style="color: #3b82f6; font-size: 3rem; margin: 0;">{similarity:.2%}</h1>
                    <p style="color: #64748b; margin: 0;">Network Similarity</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.metric("User B", compare_user)
            
            # Interpretation
            if similarity > 0.7:
                st.success("🟢 **Very High Similarity** - These candidates share most of their endorsers")
            elif similarity > 0.4:
                st.warning("🟡 **Moderate Similarity** - Some overlap in their networks")
            else:
                st.info("🔴 **Low Similarity** - Different network connections")
            
            st.markdown("**What this means:** Similarity score shows how many endorsers these two candidates have in common. High similarity might indicate candidates from the same institution or collaboration.")
    
    # ==================== USER DETAILS ====================
    st.markdown('<div class="section-header">👤 Candidate Details</div>', unsafe_allow_html=True)
    
    # Endorsement details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📥 Endorsed By")
        predecessors = list(G2.predecessors(selected_user)) if G2.has_node(selected_user) else []
        
        if predecessors:
            st.markdown(f"**{len(predecessors)} people endorsed this candidate:**")
            
            # Show in a clean list
            with st.container():
                for i, pred in enumerate(predecessors[:20], 1):
                    st.markdown(f"`{i}.` User **{pred}**")
                
                if len(predecessors) > 20:
                    with st.expander(f"Show {len(predecessors) - 20} more..."):
                        for i, pred in enumerate(predecessors[20:], 21):
                            st.markdown(f"`{i}.` User **{pred}**")
        else:
            st.info("No endorsements received")
    
    with col2:
        st.markdown("### 📤 Has Endorsed")
        successors = list(G2.successors(selected_user)) if G2.has_node(selected_user) else []
        
        if successors:
            st.markdown(f"**This candidate has endorsed {len(successors)} people:**")
            
            # Show in a clean list
            with st.container():
                for i, succ in enumerate(successors[:20], 1):
                    st.markdown(f"`{i}.` User **{succ}**")
                
                if len(successors) > 20:
                    with st.expander(f"Show {len(successors) - 20} more..."):
                        for i, succ in enumerate(successors[20:], 21):
                            st.markdown(f"`{i}.` User **{succ}**")
        else:
            st.info("Has not endorsed anyone")
    
    # Resume summary if available
    if not df.empty:
        user_row = df[df['ID'].astype(str) == selected_user]
        if not user_row.empty:
            user_idx = user_row.index[0]
            
            if 'Resume Summary' in df.columns:
                st.markdown("---")
                st.markdown("### 📄 Resume Summary")
                st.text_area(
                    "",
                    df['Resume Summary'].iloc[user_idx],
                    height=150,
                    disabled=True,
                    label_visibility="collapsed"
                )

if __name__ == "__main__":
    main()

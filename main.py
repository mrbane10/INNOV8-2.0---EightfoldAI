import streamlit as st
import networkx as nx
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import json
import csv
import pickle

# Set page layout to wide mode for better use of screen space
st.set_page_config(layout="wide")

# Function to visualize the graph using PyVis
def visualize_graph(G):
    net = Network(height="700px", width="100%", notebook=False, directed=True)
    net.barnes_hut(gravity=-80000, central_gravity=0.3, spring_length=100, spring_strength=0.001, damping=0.9)
    
    # Add nodes and edges
    pagerank = nx.pagerank(G)
    for node in G.nodes:
        net.add_node(node, size=pagerank[node]*200 + 10)
    
    for edge in G.edges:
        net.add_edge(edge[0], edge[1])
    
    # Set graph options
    net.set_options("""
    var options = {
      "nodes": {
        "scaling": {
          "min": 10,
          "max": 30
        }
      },
      "edges": {
        "color": {
          "inherit": true
        },
        "smooth": {
          "type": "continuous"
        }
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -80000,
          "springLength": 100,
          "springConstant": 0.001,
          "damping": 0.9
        },
        "minVelocity": 0.75
      }
    }
    """)
    path = "graph.html"
    net.save_graph(path)
    return path

def node_similarity(G, node1, node2):
    # You can implement any similarity measure like Jaccard, Adamic-Adar, etc.
    preds1 = set(G.predecessors(node1))
    preds2 = set(G.predecessors(node2))
    intersection = preds1 & preds2
    union = preds1 | preds2
    return len(intersection) / len(union) if len(union) > 0 else 0

# Function to detect the community for a user_id using Louvain
def get_community(G, node_id):
    communities = nx.algorithms.community.louvain_communities(G)
    for community in communities:
        if node_id in community:
            return list(community)
    return []

def load_endorsement_data(csv_path: str):
    """Load endorsement data from CSV file."""
    endorsement_data = {}
    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            user_id, recommenders = row
            endorsement_data[user_id] = json.loads(recommenders.replace("'", '"'))
    return endorsement_data

# Load data
resumes_dir = "Dataset/Final_Resumes"
recommendations_base_dir = "Dataset/Final_Recommendation_Letters"
df = pd.read_csv("./out-data/output.csv")

endorsement_data = load_endorsement_data("./Dataset/Final_Persons_And_Recommenders.csv")
G2 = nx.DiGraph()
for i in range(1000):
    G2.add_node(str(i))

for user_id, recommender_ids in endorsement_data.items():
    for recommender_id in recommender_ids:
        G2.add_edge(user_id, str(recommender_id))

# Load the directed graph from pickle file
with open("graph.pickle", "rb") as f:
    G = pickle.load(f)

# First Section: Graph Visualization
st.subheader("Graph Visualization")
graph_html_path = visualize_graph(G)
components.html(open(graph_html_path, 'r').read(), height=700)

# Add spacing between sections
st.markdown("---")

# Second Section: User Information and Options
st.subheader("User Information")

# Select a node (user_id) from the dropdown
user_ids = df['ID'].astype(str).unique()
selected_user_id = st.selectbox("Select User ID", user_ids)

st.markdown("---")

# Subsection: Ranking Candidates by Influence
st.subheader(f"Ranking Candidates by Influence for User ID {selected_user_id}")

if st.button("Rank Candidates by Influence"):
    with st.expander("Ranked Nodes"):
        pagerank = nx.pagerank(G)
        ranked_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
        st.write("Most Influential Users (Top 5):")
        for rank, (node, score) in enumerate(ranked_nodes[:5], start=1):
            st.write(f"{rank}. Node {node} - Score: {score:.4f}")
            st.write(f'Number of neighbors: {len(list(G2.neighbors(node)))}\n')

st.markdown("---")

# Subsection: Comparing Similarity Between Users
st.subheader(f"Compare Similarity Between Users for User ID {selected_user_id}")

selected_comparison_node = st.selectbox("Compare with another User ID", user_ids)
if st.button(f"Calculate Similarity between {selected_user_id} and {selected_comparison_node}"):
    with st.expander("Similarity Result"):
        similarity_score = node_similarity(G, selected_user_id, selected_comparison_node)
        st.write(f"Similarity Score between {selected_user_id} and {selected_comparison_node}: {similarity_score:.4f}")
        st.write("Note: The similarity score is calculated based on the Jaccard Index of the neighbors of the two nodes.")

st.markdown("---")

# Subsection: Display Community Details
st.subheader(f"Community Details for User ID {selected_user_id}")

if st.button("Show Community Details"):
    with st.expander("Community Information"):
        community = get_community(G, selected_user_id)
        st.write(f"Community Members for User {selected_user_id}: {community}")

st.markdown("---")

# Subsection: Neighbors and College Mates
st.subheader(f"Neighbors and College Mates for User ID {selected_user_id}")

neighbors = list(G2.neighbors(selected_user_id))
college_mates = [x for x in G.neighbors(selected_user_id) if x not in neighbors]

with st.expander("Neighbors and College Mates"):
    st.write(f"Neighbors of User {selected_user_id}: {neighbors}")
    st.write(f"College Mates of User {selected_user_id}: {college_mates}")

st.markdown("---")

# Subsection: Resume Information and Fraud Data
st.subheader(f"Resume and Fraud Information for User ID {selected_user_id}")

# Load fraud score and flag information from final.csv
fraud_data = pd.read_csv("final_df.csv")  # Assuming columns are 'ID', 'Fraud Score', 'Flag'

with st.expander("Resume Details and Fraud Information"):
    st.write(df['Resume Summary'].iloc[int(selected_user_id)])
    st.write("**Recommendation Score**:", df['Resume Score based on Recommendations'].iloc[int(selected_user_id)])
    st.write("**Suspicious Word Score**:", df['Suspicious Wording Score'].iloc[int(selected_user_id)])
    st.write("**Recommendation Redundancy Score**:", df['Recommendation Redundancy Score'].iloc[int(selected_user_id)])
    
    # Fetch fraud score and flag for the selected user
    fraud_score = fraud_data['fraud_score'].iloc[int(selected_user_id)]
    fraud_flag = fraud_data['fraud'].iloc[int(selected_user_id)]
    
    st.write("**Fraud Score**:", fraud_score)
    st.write("**Fraud Flag**:", "True" if fraud_flag else "False")


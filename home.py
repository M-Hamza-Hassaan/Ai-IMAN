import streamlit as st
import random
import folium
from streamlit_folium import folium_static

# Simulated mesh network nodes
nodes = ["Node A", "Node B", "Node C", "Node D", "Node E"]
connections = {
    "Node A": ["Node B", "Node C"],
    "Node B": ["Node A", "Node D"],
    "Node C": ["Node A", "Node E"],
    "Node D": ["Node B", "Node E"],
    "Node E": ["Node C", "Node D"]
}

# Function to process query
def process_query(query):
    return "Processed query: " + query

# Function to simulate query routing
def find_closest_node():
    return random.choice(nodes)

# Function to visualize network with Folium
def draw_network():
    # Create base map
    m = folium.Map(location=[20, 0], zoom_start=2)
    node_locations = {
        "Node A": [20, -10],
        "Node B": [25, 0],
        "Node C": [15, 5],
        "Node D": [30, 10],
        "Node E": [10, -5]
    }
    
    # Add nodes to map
    for node, loc in node_locations.items():
        folium.Marker(loc, tooltip=node, icon=folium.Icon(color='blue')).add_to(m)
    
    # Add connections
    for node, edges in connections.items():
        for edge in edges:
            folium.PolyLine([node_locations[node], node_locations[edge]], color='gray').add_to(m)
    
    folium_static(m)

# Streamlit UI
st.title("AI-Powered Mesh Networking Simulation")
st.write("This project simulates query processing and routing in a decentralized network.")

query = st.text_area("Enter your question:")
if st.button("Submit Query"):
    if query:
        st.write("### Step 1: Processing Query")
        processed_query = process_query(query)
        st.success(processed_query)
        
        st.write("### Step 2: Finding Closest Node")
        closest_node = find_closest_node()
        st.info(f"Query is routed to: {closest_node}")
        
        st.write("### Step 3: Network Visualization")
        draw_network()
        
        st.write("### Step 4: Query Response")
        st.success("Response received from " + closest_node + " (Simulated)")
    else:
        st.warning("Please enter a query.")

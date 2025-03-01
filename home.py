import streamlit as st
import random
import folium
import openai
import geopandas as gpd
from streamlit_folium import folium_static

# OpenAI API Key (Replace with your actual API key)
openai.api_key = "your-openai-api-key"

# Load Giga Geospatial Dataset (Replace with actual dataset path or URL)
@st.cache_data
def load_geospatial_data():
    # Example: Load a GeoJSON or shapefile with network nodes
    gdf = gpd.read_file("path/to/giga_dataset.geojson")
    return gdf

giga_data = load_geospatial_data()

# Extract node names and coordinates from dataset
nodes = giga_data["name"].tolist()
node_locations = {row["name"]: [row["latitude"], row["longitude"]] for _, row in giga_data.iterrows()}

# Simulated connections (or replace with real-world adjacency data)
connections = {
    node: random.sample(nodes, min(2, len(nodes))) for node in nodes
}

# AI-Powered Query Processing
def process_query(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an AI expert in geospatial networks."},
                      {"role": "user", "content": query}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI Processing Failed: {e}"

# Geospatial Routing: Find Closest Node
def find_best_node(query):
    keywords = {  
        "network": nodes[0],  
        "security": nodes[1],  
        "speed": nodes[2],  
        "connectivity": nodes[3],  
        "optimization": nodes[4]  
    }
    for keyword, node in keywords.items():
        if keyword in query.lower():
            return node
    return random.choice(nodes)

# Draw Geospatial Network
def draw_network():
    m = folium.Map(location=[20, 0], zoom_start=2)

    for node, loc in node_locations.items():
        folium.Marker(loc, tooltip=node, icon=folium.Icon(color='blue')).add_to(m)
    
    for node, edges in connections.items():
        for edge in edges:
            folium.PolyLine([node_locations[node], node_locations[edge]], color='gray').add_to(m)
    
    folium_static(m)

# Streamlit UI
st.title("AI-Powered Geospatial Mesh Network")
st.write("This project simulates AI-powered query routing in a geospatial network using Giga data.")

query = st.text_area("Enter your question:")
if st.button("Submit Query"):
    if query:
        st.write("### Step 1: AI Processing")
        processed_query = process_query(query)
        st.success(processed_query)

        st.write("### Step 2: Geospatial Routing")
        best_node = find_best_node(query)
        st.info(f"Query is routed to: {best_node} (Real-world location: {node_locations[best_node]})")

        st.write("### Step 3: Network Visualization")
        draw_network()

        st.write("### Step 4: AI Response from Node")
        st.success(f"Response from {best_node}: {processed_query}")
    else:
        st.warning("Please enter a query.")

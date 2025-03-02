import streamlit as st
import requests
import folium
import pandas as pd
import geopandas as gpd
from streamlit_folium import folium_static
from shapely.geometry import Point
from scipy.spatial import KDTree
import numpy as np
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
bagoodex_api_key = os.getenv("BAGOODEX_API_KEY")

# Load Giga Geospatial Dataset (school_geolocation.csv)
SCHOOL_DATA_FILE = "school_geolocation.csv"

@st.cache_data
def load_geospatial_data():
    df = pd.read_csv(SCHOOL_DATA_FILE)

    # Convert DataFrame to GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )
    
    return gdf

# Load school data
giga_data = load_geospatial_data()

# Extract school names and coordinates efficiently
node_locations = dict(zip(giga_data["school_name"], zip(giga_data["latitude"], giga_data["longitude"])))

# Convert coordinates to NumPy array for KDTree
school_coords = np.array(list(node_locations.values()))
school_names = list(node_locations.keys())
school_tree = KDTree(school_coords)

# Cache center location for the map
avg_lat, avg_lon = np.mean(school_coords, axis=0)

# AI-Powered Query Processing
def process_query(query, location):
    if not query:
        return "No query provided."
    
    try:
        response = requests.post(
            "https://api.aimlapi.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {bagoodex_api_key}", "Content-Type": "application/json"},
            json={"model": "bagoodex/bagoodex-search-v1", "messages": [{"role": "user", "content": query}]}
        )
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response.")
    except Exception as e:
        return f"AI Processing Failed: {e}"

# Find the Closest School
def find_best_node(lat, lon):
    _, idx = school_tree.query([lat, lon])
    return school_names[idx]

# Draw Geospatial Network
def draw_network(lat, lon):
    if not node_locations:
        st.warning("No locations available to display.")
        return

    # Create a Folium map centered at the average coordinates
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5)

    # Add school markers efficiently
    from folium.plugins import FastMarkerCluster
    locations = [[lat, lon] for lat, lon in node_locations.values()]
    FastMarkerCluster(locations).add_to(m)

    # If user provides coordinates, highlight the best node
    if lat is not None and lon is not None:
        best_node = find_best_node(lat, lon)
        best_loc = node_locations[best_node]

        folium.Marker(
            location=best_loc,
            tooltip=f"Best Match: {best_node}",
            icon=folium.Icon(color="red", icon="star")
        ).add_to(m)

    folium_static(m)

# Streamlit UI
st.title("AI-Powered Geospatial Mesh Network 🌍")
st.write("Simulating **AI-powered query routing** in a **real-world geospatial network** using Giga data.")

query = st.text_area("Enter your question:")
lat = st.number_input("Enter your latitude:", value=30.3753)  # Default: Pakistan
lon = st.number_input("Enter your longitude:", value=69.3451)

if st.button("Submit Query"):
    if query:
        st.write("### Step 1: AI Processing")
        best_node = find_best_node(lat, lon)
        processed_query = process_query(query, best_node)
        st.success(processed_query)

        st.write("### Step 2: Geospatial Routing")
        st.info(f"Query is routed to: {best_node} (Location: {node_locations[best_node]})")

        st.write("### Step 3: Network Visualization")
        draw_network(lat, lon)

        st.write("### Step 4: AI Response from Node")
        st.success(f"Response from {best_node}: {processed_query}")
    else:
        st.warning("Please enter a query.")

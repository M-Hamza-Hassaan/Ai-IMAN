import streamlit as st
import random
import requests
import folium
import openai
import geopandas as gpd
from streamlit_folium import folium_static
from shapely.geometry import Point
from scipy.spatial import KDTree
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# Load Giga Geospatial Dataset from GitHub
GIGA_DATA_URL = ""

response = requests.get(GIGA_DATA_URL)
if response.status_code == 200:
    print("URL is accessible, downloading...")
    gdf = gpd.read_file(GIGA_DATA_URL)
else:
        print(f"Failed to access URL. HTTP Status Code: {response.status_code}")


@st.cache_data
def load_geospatial_data():


    gdf = gpd.read_file(GIGA_DATA_URL)
    return gdf

giga_data = load_geospatial_data()

# Extract node names and coordinates
nodes = giga_data["name"].tolist()
node_locations = {row["name"]: [row.geometry.y, row.geometry.x] for _, row in giga_data.iterrows()}

# Build a spatial tree for fast nearest-neighbor lookup
school_coords = np.array([(row.geometry.y, row.geometry.x) for _, row in giga_data.iterrows()])
school_names = giga_data["name"].tolist()
school_tree = KDTree(school_coords)

# AI-Powered Query Processing
def process_query(query, location):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an AI expert in geospatial networks assisting schools in {location}."},
                {"role": "user", "content": query}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI Processing Failed: {e}"

# Find the Closest School Based on Query Location
def find_best_node(lat, lon):
    _, idx = school_tree.query([lat, lon])
    return school_names[idx]

# Draw Geospatial Network
def draw_network():
    m = folium.Map(location=[0, 0], zoom_start=2)  # World map

    for node, loc in node_locations.items():
        folium.Marker(
            location=loc,
            tooltip=node,
            icon=folium.Icon(color="blue")
        ).add_to(m)

    folium_static(m)

# Streamlit UI
st.title("AI-Powered Geospatial Mesh Network 🌍")
st.write("This project simulates **AI-powered query routing** in a **real-world geospatial network** using Giga data.")

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
        draw_network()

        st.write("### Step 4: AI Response from Node")
        st.success(f"Response from {best_node}: {processed_query}")
    else:
        st.warning("Please enter a query.")

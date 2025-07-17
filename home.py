from dotenv import load_dotenv
import os
import streamlit as st
import requests
import folium
import pandas as pd
import geopandas as gpd
from streamlit_folium import folium_static
from shapely.geometry import Point
from scipy.spatial import KDTree
import numpy as np
from geopy.distance import geodesic

# Load API Key
load_dotenv()
open_router_api_key = os.getenv("OPENROUTER_API_KEY")

SCHOOL_DATA_FILE = "school_geolocation.csv"

@st.cache_data
def load_geospatial_data():
    df = pd.read_csv(SCHOOL_DATA_FILE)
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )
    return gdf

# Load data
giga_data = load_geospatial_data()
node_locations = dict(zip(giga_data["school_name"], zip(giga_data["latitude"], giga_data["longitude"])))
school_coords = np.array(list(node_locations.values()))
school_names = list(node_locations.keys())
school_tree = KDTree(school_coords)
avg_lat, avg_lon = np.mean(school_coords, axis=0)

# Find Closest Node + Distance
def find_best_node(lat, lon):  # fixed arg name
    _, idx = school_tree.query([lat, lon])
    best_coords = school_coords[idx]
    distance = round(geodesic((lat, lon), best_coords).km, 2)
    return school_names[idx], distance

# AI Query Processing using OpenRouter
@st.cache_data
def process_query(query, location=None):
    if not query:
        return "No query provided."

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {open_router_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": query}]
            }
        )
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response.")
    except Exception as e:
        return f"AI Processing Failed: {e}"

# Map Drawing with Signal Circles
def draw_network(user_lat, user_lon, best_node_name):
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5)

    for name, (lat, lon) in node_locations.items():
        # Signal radius = 10km (example)
        folium.Circle(
            location=[lat, lon],
            radius=10000,
            color="blue",
            fill=True,
            fill_opacity=0.05,
            tooltip=f"{name} Signal Zone"
        ).add_to(m)

        folium.Marker(
            location=[lat, lon],
            tooltip=name,
            icon=folium.Icon(color="green", icon="info-sign")
        ).add_to(m)

    if best_node_name:
        best_loc = node_locations[best_node_name]
        folium.Marker(
            location=best_loc,
            tooltip=f"Closest Hub: {best_node_name}",
            icon=folium.Icon(color="red", icon="star")
        ).add_to(m)

    folium.Marker(
        location=[user_lat, user_lon],
        tooltip="Your Location",
        icon=folium.Icon(color="purple")
    ).add_to(m)

    folium_static(m)

# Streamlit UI
st.set_page_config(page_title="AI Geospatial Mesh Network", layout="wide")
st.title("📡 AI-Powered Geospatial Mesh Network")
st.markdown("""
This app simulates AI-assisted query routing in underprivileged areas based on **user location** and **educational hub proximity**.
""")

query = st.text_area("✍️ Enter your educational question:")
lat = st.number_input("🌍 Enter your latitude:", value=30.3753)
lon = st.number_input("🌐 Enter your longitude:", value=69.3451)
offline_mode = st.checkbox("📴 Simulate Offline Mode")

if st.button("🚀 Submit Query"):
    if not query:
        st.warning("Please enter a query.")
    else:
        with st.spinner("🔍 Finding closest node..."):
            best_node, distance = find_best_node(lat, lon)
            st.info(f"Closest Hub: **{best_node}** ({distance} km away)")

        st.write("### 🌐 Visualizing Network")
        draw_network(lat, lon, best_node)

        st.write("### 🤖 AI-Powered Response")
        if offline_mode:
            st.warning("Offline Mode Enabled. This is a cached/static response.")
            st.success("Offline Mode: Photosynthesis is the process by which plants convert sunlight into energy.")
        else:
            with st.spinner("Processing with AI..."):
                response = process_query(query, best_node)
            if "AI Processing Failed" in response:
                st.error(response)
            else:
                st.success(response)
                st.write("Response from AI:", response)
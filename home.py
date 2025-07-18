import os
import requests
import folium
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from scipy.spatial import KDTree
from geopy.distance import geodesic
from streamlit_folium import st_folium
from dotenv import load_dotenv
import streamlit as st

# Load API Key
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SCHOOL_DATA_FILE = "school_geolocation.csv"

# ---------------------- CACHE SCHOOL DATA ----------------------
@st.cache_data
def load_geospatial_data():
    df = pd.read_csv(SCHOOL_DATA_FILE)
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )
    return gdf

# ---------------------- CORE LOCATION LOGIC ----------------------
giga_data = load_geospatial_data()
node_locations = dict(zip(giga_data["school_name"], zip(giga_data["latitude"], giga_data["longitude"])))
school_coords = np.array(list(node_locations.values()))
school_names = list(node_locations.keys())
school_tree = KDTree(school_coords)

def find_closest_node(lat, lon):
    _, idx = school_tree.query([lat, lon])
    closest_coords = school_coords[idx]
    distance_km = round(geodesic((lat, lon), closest_coords).km, 2)
    return school_names[idx], distance_km

# ---------------------- AI QUERY PROCESSING ----------------------
@st.cache_data
def get_ai_response(query):
    if not query:
        return "No query provided."
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": query}]
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI failed: {e}"

# ---------------------- MAP DRAWING ----------------------
def draw_map(user_lat, user_lon, best_node_name, radius_km):
    m = folium.Map(location=[user_lat, user_lon], zoom_start=7)

    for name, (lat, lon) in node_locations.items():
        distance = geodesic((user_lat, user_lon), (lat, lon)).km
        if distance <= radius_km:
            folium.Circle(
                location=[lat, lon],
                radius=10000,
                color="blue",
                fill=True,
                fill_opacity=0.07,
                tooltip=f"{name} Signal Area"
            ).add_to(m)
            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(color="green"),
                tooltip=name
            ).add_to(m)

    folium.Marker(
        location=node_locations[best_node_name],
        icon=folium.Icon(color="red", icon="star"),
        tooltip=f"Closest Hub: {best_node_name}"
    ).add_to(m)

    folium.Marker(
        location=[user_lat, user_lon],
        icon=folium.Icon(color="purple"),
        tooltip="You"
    ).add_to(m)

    _ = st_folium(m, height=500, width=900)

# ---------------------- APP SETUP ----------------------
st.set_page_config(page_title="📡 Education Mesh for Children", layout="wide")
st.title("📡 AI-Powered Learning Assistant for Underserved Communities")
st.markdown("Designed to guide underserved children by connecting them to nearby learning hubs and providing AI-powered educational help.")

# ---------------------- SESSION STATE INIT ----------------------
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "response" not in st.session_state:
    st.session_state.response = ""
if "best_node" not in st.session_state:
    st.session_state.best_node = ""
if "distance" not in st.session_state:
    st.session_state.distance = 0.0

# ---------------------- USER INPUT ----------------------
st.subheader("✍️ Ask Your Question")
query = st.text_area("What do you want to learn about?", placeholder="E.g. What is photosynthesis?")

st.subheader("📍 Your Location")
lat = st.number_input("Latitude", value=30.3753)
lon = st.number_input("Longitude", value=69.3451)
radius_km = st.slider("Signal radius (km)", 10, 500, 100, 10)
st.caption("⚠️ Increasing the radius may slow down map rendering.")

suggestions = st.expander("🧠 Try Suggested Topics")
with suggestions:
    st.markdown("- What is the water cycle?\n- How do plants grow?\n- What is 2 + 2?\n- Why is the sky blue?\n- What are continents?")

# ---------------------- FORM SUBMISSION ----------------------
if st.button("🚀 Submit"):
    st.session_state.submitted = True
    st.session_state.best_node, st.session_state.distance = find_closest_node(lat, lon)
    if query.strip():
        enhanced_prompt = f"A child asked: {query.strip()}. Explain it in a simple way suitable for grade 5."
        st.session_state.response = get_ai_response(enhanced_prompt)

# ---------------------- RESET ----------------------
if st.button("🔄 Reset"):
    for key in st.session_state.keys():
        st.session_state[key] = False if isinstance(st.session_state[key], bool) else ""

# ---------------------- RESULTS ----------------------
if st.session_state.submitted:
    st.success(f"✅ Closest Hub: **{st.session_state.best_node}** ({st.session_state.distance} km away)")
    st.write("### 🗺️ Learning Network Map")
    
    with st.spinner("Loading map..."):
        draw_map(lat, lon, st.session_state.best_node, radius_km)

    if query:
        st.write("### 🤖 AI Response")
        st.success(st.session_state.response)

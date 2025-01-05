import streamlit as st
import folium
from streamlit_folium import st_folium
from app.utils.api_client import APIClient


def heatmap_page():
    st.title("Disease Heatmap")
    st.write("Visualize disease clusters and reported points.")
    client = APIClient()

    # Filter options
    filter_type = st.selectbox(
        "Select a filter type:",
        ["By Days", "By Location", "Seasonal Clusters", "Nearby Points"]
    )

    params = {}
    if filter_type == "By Days":
        params["days"] = st.number_input("Enter the number of days:", min_value=1, value=30)
    elif filter_type == "By Location":
        params["latitude"] = st.number_input("Enter Latitude:", value=34.0522)
        params["longitude"] = st.number_input("Enter Longitude:", value=-118.2437)
        params["radius"] = st.number_input("Enter Radius (in km):", min_value=1, value=10)
    elif filter_type == "Seasonal Clusters":
        params["seasonal"] = st.selectbox("Seasonal Analysis:", [0, 1], format_func=lambda x: "Off" if x == 0 else "On")
        params["clusters"] = st.number_input("Number of Clusters:", min_value=1, value=1)
    elif filter_type == "Nearby Points":
        params["latitude"] = st.number_input("Enter Latitude:", value=37.7749)
        params["longitude"] = st.number_input("Enter Longitude:", value=-122.4194)
        params["radius"] = st.number_input("Enter Radius (in km):", min_value=1, value=10)
        params["days"] = st.number_input("Enter the number of days:", min_value=1, value=30)

    # Initialize an empty map to display by default
    map_obj = folium.Map(location=[13.01654, 77.57069], zoom_start=8)  # Default location: Los Angeles

    # Fetch data from the API
    if st.button("Fetch Heatmap Data"):
        heatmap_data = client.get_heatmap_data(filter_type.lower().replace(" ", "_"), **params)
        if isinstance(heatmap_data, dict):
            # Update map with fetched data
            map_obj = create_heatmap(heatmap_data)
            st.success("Heatmap data loaded successfully!")
        else:
            st.error(f"Failed to fetch data: {heatmap_data}")

    # Display the map
    st_data = st_folium(map_obj, width=700, height=500)


def create_heatmap(data):
    """
    Create a folium map with clusters and individual points from data.
    """
    if "clusters" in data and data["clusters"]:
        # Center map on the first cluster's location
        center = data["clusters"][0]["center"]
        map_obj = folium.Map(location=[center["latitude"], center["longitude"]], zoom_start=10)
    else:
        # Default center if no clusters are available
        map_obj = folium.Map(location=[13.01654, 77.57069], zoom_start=8)

    # Add clusters to the map
    for cluster in data.get("clusters", []):
        folium.CircleMarker(
            location=[cluster["center"]["latitude"], cluster["center"]["longitude"]],
            radius=cluster["size"] * 2,
            color="red",
            fill=True,
            fill_opacity=0.6,
            tooltip=f"Cluster ID: {cluster['cluster_id']}<br>Diseases: {cluster['diseases']}"
        ).add_to(map_obj)

    # Add individual points to the map
    for point in data.get("points", []):
        folium.CircleMarker(
            location=[point["latitude"], point["longitude"]],
            radius=4,
            color=point["color"],
            fill=True,
            fill_opacity=0.6,
            tooltip=f"Disease: {point['disease']}<br>Confidence: {point['confidence']:.2f}"
        ).add_to(map_obj)

    return map_obj

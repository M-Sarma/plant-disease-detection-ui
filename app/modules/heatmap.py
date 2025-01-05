import streamlit as st
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium
import json
from app.utils.api_client import APIClient

# Utility function to sanitize data
def sanitize_keys(data):
    if isinstance(data, dict):
        return {str(k): sanitize_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_keys(i) for i in data]
    else:
        return data

# Function to create heatmap
def create_heatmap(data):
    try:
        # Initialize map with default center
        map_obj = folium.Map(location=[34.0522, -118.2437], zoom_start=8, tiles="cartodbpositron")

        # Add clusters
        if "clusters" in data and data["clusters"]:
            for cluster in data["clusters"]:
                lat = cluster["center"]["latitude"]
                lon = cluster["center"]["longitude"]
                size = cluster.get("size", 10)
                diseases = cluster.get("diseases", {})

                # Create popup with cluster information
                popup_content = f"<b>Cluster ID:</b> {cluster.get('cluster_id')}<br>"
                popup_content += f"<b>Size:</b> {size}<br>"
                popup_content += f"<b>Diseases:</b> {', '.join(f'{k}: {v}' for k, v in diseases.items())}"

                folium.CircleMarker(
                    location=[lat, lon],
                    radius=max(size, 10),  # Scale size
                    color="#FF0000",
                    fill=True,
                    fill_opacity=0.6,
                    popup=popup_content
                ).add_to(map_obj)

        # Add points to heatmap
        heat_data = [
            [point["latitude"], point["longitude"], point.get("confidence", 1.0)]
            for point in data.get("points", [])
        ]
        if heat_data:
            HeatMap(heat_data, min_opacity=0.5, radius=15, blur=10).add_to(map_obj)

        return map_obj
    except Exception as e:
        st.error(f"Error in create_heatmap: {str(e)}")
        raise e


def heatmap_page():
    st.title("Disease Heatmap")
    st.write("Visualize disease clusters and reported points.")

    client = APIClient()

    # Initialize session state for heatmap data
    if "heatmap_data" not in st.session_state:
        st.session_state.heatmap_data = None

    # Filter options in a sidebar
    with st.sidebar:
        filter_type = st.selectbox(
            "Select a filter type:",
            ["By Days", "By Location", "Seasonal Clusters", "Nearby Points"]
        )

        params = {}
        if filter_type == "By Days":
            params["days"] = int(st.number_input("Enter the number of days:", min_value=1, value=30))
        elif filter_type == "By Location":
            params["latitude"] = float(st.number_input("Enter Latitude:", value=34.0522))
            params["longitude"] = float(st.number_input("Enter Longitude:", value=-118.2437))
            params["radius"] = float(st.number_input("Enter Radius (in km):", min_value=1, value=10))
        elif filter_type == "Seasonal Clusters":
            params["seasonal"] = int(
                st.selectbox("Seasonal Analysis:", [0, 1], format_func=lambda x: "Off" if x == 0 else "On"))
            params["clusters"] = int(st.number_input("Number of Clusters:", min_value=1, value=1))
        elif filter_type == "Nearby Points":
            params["latitude"] = float(st.number_input("Enter Latitude:", value=37.7749))
            params["longitude"] = float(st.number_input("Enter Longitude:", value=-122.4194))
            params["radius"] = float(st.number_input("Enter Radius (in km):", min_value=1, value=10))
            params["days"] = int(st.number_input("Enter the number of days:", min_value=1, value=30))

    # Fetch data only when button is clicked
    if st.sidebar.button("Fetch Heatmap Data", type="primary"):
        with st.spinner("Fetching and processing data..."):
            try:
                heatmap_data = client.get_heatmap_data(filter_type.lower().replace(" ", "_"), **params)
                if not heatmap_data or not isinstance(heatmap_data, dict):
                    raise ValueError("No data returned from the API or invalid format.")

                st.session_state.heatmap_data = heatmap_data  # Save data to session state
                st.success("Heatmap data fetched successfully!")
            except Exception as e:
                st.error(f"Error fetching data: {str(e)}")
                st.session_state.heatmap_data = None

    # Render the heatmap if data exists
    if st.session_state.heatmap_data:
        try:
            map_obj = create_heatmap(st.session_state.heatmap_data)
            st_folium(map_obj, width=800, height=600)
        except Exception as e:
            st.error(f"Error rendering heatmap: {str(e)}")
    else:
        # Display an initial empty map
        initial_map = folium.Map(location=[34.0522, -118.2437], zoom_start=8)
        st_folium(initial_map, width=800, height=600)


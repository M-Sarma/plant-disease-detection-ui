import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
from app.utils.api_client import APIClient
import json


def create_heatmap(data):
    """
    Create a folium map with clusters and individual points from data.
    """
    try:
        # Debug print
        st.write("Raw data received:", json.dumps(data, indent=2))

        # Set initial map center
        center_lat, center_lon = 13.01654, 77.57069
        if data.get("clusters") and len(data["clusters"]) > 0:
            center_lat = float(data["clusters"][0]["center"]["latitude"])
            center_lon = float(data["clusters"][0]["center"]["longitude"])

        st.write(f"Map center: {center_lat}, {center_lon}")

        # Create the base map
        map_obj = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,  # Increased zoom level
            tiles='cartodbpositron'
        )

        # Process points for heatmap
        if data.get("points"):
            heat_data = []
            for point in data["points"]:
                try:
                    lat = float(point["latitude"])
                    lon = float(point["longitude"])
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        # Increased weight for better visibility
                        heat_data.append([lat, lon, 10.0])
                except (ValueError, TypeError):
                    continue

            st.write(f"Number of valid heat points: {len(heat_data)}")
            if heat_data:
                st.write("Sample heat points:", heat_data[:3])

                # Create heatmap with more pronounced parameters
                plugins.HeatMap(
                    data=heat_data,
                    min_opacity=0.5,  # Increased from 0.4
                    max_opacity=1.0,  # Increased from 0.8
                    radius=25,  # Increased from 15
                    blur=15,  # Increased from 10
                    gradient={
                        0.2: '#87CEEB',  # Light blue
                        0.4: '#FFFF00',  # Yellow
                        0.6: '#FFA500',  # Orange
                        0.8: '#FF0000',  # Red
                        1.0: '#8B0000'  # Dark red
                    }
                ).add_to(map_obj)

        # Add cluster markers
        if data.get("clusters"):
            st.write(f"Processing {len(data['clusters'])} clusters")
            for cluster in data["clusters"]:
                try:
                    lat = float(cluster["center"]["latitude"])
                    lon = float(cluster["center"]["longitude"])
                    size = float(cluster.get("size", 10))

                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        # Create more visible cluster markers
                        folium.CircleMarker(
                            location=[lat, lon],
                            radius=max(size * 3, 20),  # Increased size
                            color='#FF0000',
                            weight=3,
                            fill=True,
                            fill_opacity=0.8,
                            popup=f"""
                                <b>Cluster {cluster.get('cluster_id', 'N/A')}</b><br>
                                Size: {size}<br>
                                Lat: {lat:.4f}<br>
                                Lon: {lon:.4f}
                            """
                        ).add_to(map_obj)

                        st.write(f"Added cluster marker at {lat}, {lon}")
                except (ValueError, TypeError, KeyError) as e:
                    st.warning(f"Skipped invalid cluster: {str(e)}")

        return map_obj

    except Exception as e:
        st.error(f"Error in create_heatmap: {str(e)}")
        raise e


def heatmap_page():
    st.title("Disease Heatmap")
    st.write("Visualize disease clusters and reported points.")
    client = APIClient()

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

    # Create columns for map and debug info
    col1, col2 = st.columns([7, 3])

    # Initialize an empty map with default center
    initial_map = folium.Map(location=[13.01654, 77.57069], zoom_start=8)

    # Fetch data from the API
    if st.sidebar.button("Fetch Heatmap Data", type="primary"):
        with st.spinner("Fetching and processing data..."):
            try:
                heatmap_data = client.get_heatmap_data(filter_type.lower().replace(" ", "_"), **params)

                # Debug: Print raw API response
                st.write("API Response:", json.dumps(heatmap_data, indent=2))

                with col2:
                    st.write("#### Debug Information")
                    st.write("Parameters:", params)
                    if isinstance(heatmap_data, dict):
                        st.write("Points:", len(heatmap_data.get("points", [])))
                        st.write("Clusters:", len(heatmap_data.get("clusters", [])))
                        # Print first point and cluster for debugging
                        if heatmap_data.get("points"):
                            st.write("Sample point:", heatmap_data["points"][0])
                        if heatmap_data.get("clusters"):
                            st.write("Sample cluster:", heatmap_data["clusters"][0])

                if isinstance(heatmap_data, dict):
                    map_obj = create_heatmap(heatmap_data)
                    with col1:
                        st_folium(map_obj, width=800, height=600)
                    st.success("Heatmap data loaded successfully!")
                else:
                    st.error(f"Failed to fetch data: {heatmap_data}")
                    with col1:
                        st_folium(initial_map, width=800, height=600)
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")
                st.exception(e)  # This will print the full traceback
                with col1:
                    st_folium(initial_map, width=800, height=600)
    else:
        # Display initial map if no data is fetched yet
        with col1:
            st_folium(initial_map, width=800, height=600)
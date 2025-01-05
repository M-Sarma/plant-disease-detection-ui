import streamlit as st

def collect_geolocation():
    lat = st.text_input("Latitude", placeholder="Enter latitude")
    lon = st.text_input("Longitude", placeholder="Enter longitude")
    return {"latitude": lat, "longitude": lon}

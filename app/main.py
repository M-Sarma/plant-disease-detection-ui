import sys
import os
import streamlit as st
from modules.predict import predict_page
from modules.heatmap import heatmap_page

st.set_page_config(page_title="Plant Disease Detection App")
# Add the project root directory to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Sidebar Navigation
st.sidebar.title("Plant Disease Detection")
page = st.sidebar.radio("Navigate", ["Predict", "Heatmap"])

if page == "Predict":
    predict_page()
elif page == "Heatmap":
    heatmap_page()

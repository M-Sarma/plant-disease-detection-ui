import sys
import os
import streamlit as st
from app.modules.predict import predict_page
from app.modules.heatmap import heatmap_page

# Add the project root directory to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Sidebar Navigation
st.sidebar.title("Plant Disease Detection")
page = st.sidebar.radio("Navigate", ["Predict", "Heatmap"])

if page == "Predict":
    predict_page()
elif page == "Heatmap":
    heatmap_page()

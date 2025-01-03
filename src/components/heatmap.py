import streamlit as st
import pandas as pd
from utils.api_client import APIClient

class HeatmapComponent:
    def __init__(self):
        self.api_client = APIClient()

    def render(self):
        st.subheader("Disease Spread Heatmap")
        
        filters = {
            'timeframe': st.selectbox("Time Period", ["Last Week", "Last Month", "Last Year"]),
            'disease_type': st.multiselect("Disease Types", ["Blight", "Rust", "Mildew"])
        }
        
        try:
            heatmap_data = self.api_client.get_heatmap_data(filters)
            if heatmap_data:
                df = pd.DataFrame(heatmap_data)
                st.map(df)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Active Hotspots", len(df))
                with col2:
                    st.metric("Risk Level", "Medium")
        except Exception as e:
            st.error(f"Error loading heatmap: {str(e)}")

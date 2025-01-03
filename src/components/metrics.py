import streamlit as st

from src.utils.api_client import APIClient


class MetricsComponent:
    def __init__(self):
        self.api_client = APIClient()

    def render(self):
        st.subheader("System Metrics")
        
        try:
            metrics = self.api_client.get_metrics()
            if metrics:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Scans", metrics['total_scans'])
                    st.metric("Success Rate", f"{metrics['success_rate']}%")
                with col2:
                    st.metric("Active Users", metrics['active_users'])
                    st.metric("Response Time", f"{metrics['avg_response_time']}s")
                with col3:
                    st.metric("Disease Types", metrics['disease_types'])
                    st.metric("Accuracy", f"{metrics['accuracy']}%")
        except Exception as e:
            st.error(f"Error loading metrics: {str(e)}")

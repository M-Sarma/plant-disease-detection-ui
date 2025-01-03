import streamlit as st
from config import AppConfig
from components.prediction import PredictionComponent
from components.heatmap import HeatmapComponent
from components.metrics import MetricsComponent


class PlantDiseaseUI:
    def __init__(self):
        self.config = AppConfig()
        self.setup_page_config()
        self.components = {
            'prediction': PredictionComponent(),
            'heatmap': HeatmapComponent(),
            'metrics': MetricsComponent()
        }

    def setup_page_config(self):
        st.set_page_config(
            page_title="Plant Disease Identification",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    def run(self):
        st.title("Plant Disease Identification")
        menu = ["Home", "Disease Prediction", "Heatmap", "Metrics"]
        choice = st.sidebar.selectbox("Navigation", menu)

        if choice == "Home":
            self.render_home()
        elif choice == "Disease Prediction":
            self.components['prediction'].render()
        elif choice == "Heatmap":
            self.components['heatmap'].render()
        elif choice == "Metrics":
            self.components['metrics'].render()

    def render_home(self):
        st.header("Welcome to Plant Disease Identification")
        st.write("""
        Upload plant images to identify diseases and get treatment recommendations.
        Use our interactive heatmap to track disease spread in your region.
        """)

if __name__ == "__main__":
    app = PlantDiseaseUI()
    app.run()

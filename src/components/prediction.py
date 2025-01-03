import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from PIL import Image
import requests
from utils.api_client import APIClient

class PredictionComponent:
    def __init__(self):
        self.api_client = APIClient()

    def handle_image_upload(self):
        image_source = st.radio("Select Image Source", ("Upload Image", "Capture from Camera"))
        if image_source == "Upload Image":
            return st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        return st.camera_input("Take a photo")

    def process_prediction(self, image_file, location_data):
        try:
            response = self.api_client.predict(image_file, location_data)
            if response:
                self.display_results(response)
                return response['id'], response['classification']
            return None, None
        except Exception as e:
            st.error(f"Error processing prediction: {str(e)}")
            return None, None

    def display_results(self, data):
        st.subheader("Diagnosis Results")
        confidence = round(data['classification']['confidence'] * 100, 2)
        st.metric("Confidence Score", f"{confidence}%")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"""
            **Disease:** {data['classification']['class_name']}
            **Description:** {data['disease_details']['description']}
            **Treatment:** {" ".join(data['disease_details']['solutions'])}
            """)
        with col2:
            st.subheader("Suggestions")
            for suggestion in data['suggestions']:
                st.write(f"• {suggestion}")

    def render(self):
        st.subheader("Disease Prediction")
        uploaded_image = self.handle_image_upload()
        
        if uploaded_image:
            st.image(uploaded_image, caption="Selected Image", use_column_width=True)
            location_data = streamlit_geolocation()
            
            if location_data['latitude'] and st.button("Analyze Image"):
                self.process_prediction(uploaded_image, location_data)

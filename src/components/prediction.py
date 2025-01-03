import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from PIL import Image
import requests
import traceback

from src.utils.api_client import APIClient


class PredictionComponent:
    def __init__(self):
        self.api_client = APIClient()
        # Initialize session state variables if they don't exist
        if 'prediction_id' not in st.session_state:
            st.session_state.prediction_id = None
        if 'original_prediction' not in st.session_state:
            st.session_state.original_prediction = None
        if 'feedback_submitted' not in st.session_state:
            st.session_state.feedback_submitted = False

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
            traceback_str = traceback.format_exc()
            print(traceback_str)
            return None, None

    def submit_feedback(self, prediction_id, original_prediction, feedback_type, selected_class=None):
        try:
            feedback_data = {
                "id": prediction_id,
                "original_prediction": original_prediction,
                "user_feedback": feedback_type.lower(),
                "user_suggestion": selected_class if selected_class else None
            }

            response = self.api_client.submit_feedback(
                prediction_id=feedback_data["id"],
                original_prediction=feedback_data["original_prediction"],
                user_feedback=feedback_data["user_feedback"],
                user_suggestion=feedback_data["user_suggestion"]
            )

            if isinstance(response, dict):
                st.session_state.feedback_submitted = True
                st.success("Thank you for your feedback!")
            else:
                st.error("Error submitting feedback. Please try again.")

        except Exception as e:
            st.error(f"Error submitting feedback: {str(e)}")
            traceback_str = traceback.format_exc()
            print(traceback_str)

    def display_results(self, data):
        # Store prediction data in session state
        st.session_state.prediction_id = data['id']
        st.session_state.original_prediction = {
            "class": data['classification']['class_name'],
            "confidence": data['classification']['confidence']
        }

        st.subheader("Diagnosis Results")
        confidence = round(data['classification']['confidence'] * 100, 2)

        # Confidence and Disease Information
        st.metric("Confidence Score", f"{confidence}%")
        st.markdown(f"**Disease:** {data['classification']['class_name']}")

        # Disease Details
        st.markdown("### Disease Details")
        st.write("**Description:**")
        st.write(data['disease_details']['description'])
        st.write("**Treatment:**")
        for solution in data['disease_details']['solutions']:
            st.write(f"- {solution}")

        # Suggestions Section
        st.markdown("### Suggestions")
        if data.get('suggestions'):
            for suggestion in data['suggestions']:
                st.write(f"• {suggestion}")

        # Feedback Section
        if not st.session_state.feedback_submitted:
            st.markdown("---")
            st.markdown("### Feedback")

            feedback_col1, feedback_col2 = st.columns([2, 1])

            with feedback_col1:
                feedback_choice = st.radio(
                    "Was the disease classification accurate?",
                    options=["Positive", "Negative"],
                    horizontal=True,
                    key="feedback_radio"
                )

            selected_class = None
            if feedback_choice == "Negative":
                st.markdown("#### Select the Correct Disease")
                if data.get("feedback_prompt_list"):
                    options = [item['class_name'] for item in data["feedback_prompt_list"]]
                    selected_class = st.selectbox(
                        "Alternative Options",
                        options=options,
                        key="feedback_select"
                    )
                else:
                    st.warning("No alternative classification available")

            with feedback_col2:
                if st.button("Submit Feedback", key="submit_feedback"):
                    self.submit_feedback(
                        st.session_state.prediction_id,
                        st.session_state.original_prediction,
                        feedback_choice,
                        selected_class
                    )

    def render(self):
        st.subheader("Disease Prediction")
        uploaded_image = self.handle_image_upload()

        if uploaded_image:
            st.image(uploaded_image, caption="Selected Image", use_container_width=True)
            location_data = streamlit_geolocation()

            if st.button("Analyze Image"):
                self.process_prediction(uploaded_image, location_data)
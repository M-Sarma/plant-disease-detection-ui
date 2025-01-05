import streamlit as st
from app.utils.api_client import APIClient

def feedback_page():
    st.title("Submit Feedback")
    client = APIClient()

    if "prediction_data" in st.session_state:
        prediction_data = st.session_state.prediction_data
        feedback_prompt = prediction_data["feedback_prompt_list"]
        prediction_id = prediction_data["id"]

        # Feedback Form
        user_feedback = st.radio("Was this prediction accurate?", ["Positive", "Negative"])
        user_suggestion = st.selectbox(
            "Suggest a Correct Classification:",
            [item["class_name"][0] for item in feedback_prompt]
        )

        if st.button("Submit Feedback"):
            feedback_response = client.submit_feedback(
                prediction_id=prediction_id,
                original_prediction=prediction_data["classification"],
                user_feedback=user_feedback.lower(),
                user_suggestion=user_suggestion
            )
            if isinstance(feedback_response, dict):
                st.success("Thank you for your feedback!")
            else:
                st.error("Failed to submit feedback. Please try again.")
    else:
        st.warning("No prediction data available. Please make a prediction first.")

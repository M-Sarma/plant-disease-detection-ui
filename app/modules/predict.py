import streamlit as st
from app.utils.api_client import APIClient
from app.components.image_uploader import upload_or_capture_image
from app.components.geolocation import collect_geolocation

def predict_page():
    st.title("Plant Disease Prediction")
    client = APIClient()

    # Upload or Capture Image
    image = upload_or_capture_image()
    location = collect_geolocation()

    # Show Prediction Results
    if st.button("Predict"):
        if image:
            prediction_response = client.predict(image_file=image, location_data=location)

            classification = prediction_response["classification"]
            disease_details = prediction_response["disease_details"]

            st.write("### Prediction Results")
            st.write(f"**Class Name:** {classification['class_name']}")
            st.write(f"**Confidence:** {classification['confidence']:.2f}")
            st.write(f"**Description:** {disease_details['description']}")
            st.write("**Solutions:**")
            for solution in disease_details["solutions"]:
                st.write(f"- {solution}")

            # Store prediction in session state
            st.session_state.prediction_data = prediction_response
            st.session_state.user_feedback = None  # Reset feedback
            st.session_state.user_suggestion = None  # Reset classification suggestion
        else:
            st.error("Please upload an image to continue.")

    # Feedback Section (only if prediction exists)
    if "prediction_data" in st.session_state:
        st.write("### Submit Feedback")
        prediction_data = st.session_state.prediction_data
        feedback_prompt = prediction_data["feedback_prompt_list"]
        prediction_id = prediction_data["id"]

        # Feedback Form
        user_feedback = st.radio(
            "Was this prediction accurate?",
            ["Positive", "Negative"],
            index=0 if st.session_state.get("user_feedback") is None else
                    ["Positive", "Negative"].index(st.session_state["user_feedback"]),
            key="user_feedback"
        )

        # Reset classification suggestion if feedback changes
        if user_feedback == "Positive" and st.session_state.get("user_suggestion") is not None:
            st.session_state.user_suggestion = None

        # Show "Suggest a Correct Classification" only if Negative is selected
        if user_feedback == "Negative":
            user_suggestion = st.selectbox(
                "Suggest a Correct Classification:",
                [item["class_name"][0] for item in feedback_prompt],
                key="user_suggestion"
            )

        if st.button("Submit Feedback"):
            feedback_response = client.submit_feedback(
                prediction_id=prediction_id,
                original_prediction=prediction_data["classification"],
                user_feedback=user_feedback.lower(),
                user_suggestion=st.session_state.get("user_suggestion")  # Pass only if selected
            )
            if isinstance(feedback_response, dict):
                st.success("Thank you for your feedback!")
            else:
                st.error("Failed to submit feedback. Please try again.")

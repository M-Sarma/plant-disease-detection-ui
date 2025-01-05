import streamlit as st
from streamlit_geolocation import streamlit_geolocation

from app.utils.api_client import APIClient
from app.utils.confidence_gradient_bar import create_gradient_bar


def predict_page():
    st.title("Plant Disease Prediction")
    client = APIClient()

    # Image Upload Section
    st.write("### Upload or Capture an Image")
    image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    show_camera = st.button("Open Camera to Take Picture")
    if show_camera:
        image = st.camera_input("Take a photo")

    # Display the uploaded or captured image
    if image is not None:
        st.image(image, caption="Selected Image", use_container_width=True)

    # Geolocation Section
    st.write("### Capture Your Location (Optional)")
    location = streamlit_geolocation()  # Using streamlit-geolocation
    location_data = {"latitude": None, "longitude": None}

    if location and isinstance(location, dict):
        try:
            latitude = round(float(location.get('latitude', 0)), 5)
            longitude = round(float(location.get('longitude', 0)), 5)

            location_data = {
                'latitude': latitude,
                'longitude': longitude
            }
            st.write(f"*Captured location:* {location_data}")

        except (TypeError, ValueError):
            st.error("Could not get valid location coordinates")
    else:
        st.warning("Click the button above to capture location if needed.")

    # Prediction Button
    st.write("### Make a Prediction")
    if st.button("Predict"):
        if image is not None:
            prediction_response = client.predict(image_file=image, location_data=location_data)

            if "error" in prediction_response:
                st.error(prediction_response["error"])

            else:
                classification = prediction_response["classification"]
                disease_details = prediction_response["disease_details"]

                st.write("### Prediction Results")
                st.write(f"**Class Name:** {classification['class_name']}")
                st.write(f"**Confidence:**")
                create_gradient_bar(classification['confidence'] * 100)
                st.write(f"**Description:** {disease_details['description']}")
                st.write(f"**Causes:** {disease_details['causes']}")
                st.write("**Solutions:**")
                for solution in disease_details["solutions"]:
                    st.write(f"- {solution}")

                # Store prediction in session state
                st.session_state.prediction_data = prediction_response
                st.session_state.user_feedback = None  # Reset feedback
                st.session_state.user_suggestion = None  # Reset classification suggestion
        else:
            st.error("Please upload or capture an image.")

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

            if "error" in feedback_response:
                st.error(feedback_response["error"])

            if isinstance(feedback_response, dict):
                st.success("Thank you for your feedback!")

            else:
                st.error("Failed to submit feedback. Please try again.")

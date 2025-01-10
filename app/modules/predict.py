import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from utils.api_client import APIClient
from utils.confidence_gradient_bar import create_gradient_bar


def predict_page():
    st.title("Plant Disease Prediction")
    client = APIClient()

    # Initialize session state for image and input method
    if "captured_image" not in st.session_state:
        st.session_state.captured_image = None
    if "input_method" not in st.session_state:
        st.session_state.input_method = None

    # Image Upload Section
    st.write("### Upload or Capture an Image")

    # Method selection with radio buttons instead of regular buttons
    input_method = st.radio(
        "Choose input method:",
        ("Upload Image", "Take Picture"),
        horizontal=True
    )

    # Display appropriate input method based on selection
    if input_method == "Upload Image":
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=["jpg", "jpeg", "png"],
            key="file_uploader"
        )
        if uploaded_file:
            st.session_state.captured_image = uploaded_file
            st.session_state.input_method = "upload"

    else:  # Take Picture option
        camera_image = st.camera_input("Take a photo")
        if camera_image:
            st.session_state.captured_image = camera_image
            st.session_state.input_method = "camera"

    # Display Section
    st.write("### Selected Image")
    if st.session_state.captured_image is not None:
        st.image(
            st.session_state.captured_image,
            caption="Selected Image",
            use_container_width=True
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            # Clear button
            if st.button("Clear Image"):
                st.session_state.captured_image = None
                st.session_state.input_method = None
    else:
        st.warning("No image uploaded or captured yet.")

    # Geolocation Section
    st.write("### Capture Your Location (Optional)")
    location = streamlit_geolocation()  # Using streamlit-geolocation
    location_data = {"latitude": None, "longitude": None}

    if location and isinstance(location, dict):
        try:
            location_data = {
                "latitude": round(float(location.get("latitude", 0)), 5),
                "longitude": round(float(location.get("longitude", 0)), 5),
            }
            st.write(f"*Captured location:* {location_data}")
        except (TypeError, ValueError):
            st.error("Click the button above to capture location if needed.")
    else:
        st.warning("Click the button above to capture location if needed.")

    # Prediction Button
    st.write("### Make a Prediction")
    if st.button("Predict"):
        if st.session_state.captured_image is not None:
            prediction_response = client.predict(
                image_file=st.session_state.captured_image, location_data=location_data
            )
            if "error" in prediction_response:
                st.error(prediction_response["error"])
            else:
                classification = prediction_response["classification"]

                # Check if the plant is healthy
                if "healthy" in classification["class_name_internal"].lower():
                    display_name = classification['class_name_internal'].replace('___', ' - ').replace('_', ' ')
                    st.write(f"**Class Name:** {display_name}")
                    st.write(f"**Confidence:**")
                    create_gradient_bar(classification["confidence"] * 100)
                    st.success("✅ Good news! No disease detected. Your plant appears to be healthy.")
                    st.write("""
                                    **Recommendations to maintain plant health:**
                                    - Continue regular watering and fertilization schedule
                                    - Monitor for any changes in leaf color or texture
                                    - Maintain good air circulation
                                    - Keep the growing environment clean
                                    - Regular pruning of dead or yellowing leaves
                                    """)
                else:
                    disease_details = prediction_response["disease_details"]
                    st.write("### Prediction Results")
                    st.write(f"**Class Name:** {classification['class_name']}")
                    st.write(f"**Confidence:**")
                    create_gradient_bar(classification["confidence"] * 100)
                    st.write(f"**Description:** {disease_details['description']}")
                    st.write(f"**Causes:** {disease_details['causes']}")
                    st.write("**Solutions:**")
                    for solution in disease_details["solutions"]:
                        st.write(f"- {solution}")

                # Store prediction in session state
                st.session_state.prediction_data = prediction_response
                st.session_state.user_feedback = None
                st.session_state.user_suggestion = None
        else:
            st.error("Please upload or capture an image.")

    # Feedback Section
    if "prediction_data" in st.session_state:
        st.write("### Submit Feedback")
        prediction_data = st.session_state.prediction_data
        feedback_prompt = prediction_data["feedback_prompt_list"]
        prediction_id = prediction_data["id"]

        user_feedback = st.radio(
            "Was this prediction accurate?",
            ["Positive", "Negative"],
            index=0 if st.session_state.get("user_feedback") is None else
            ["Positive", "Negative"].index(st.session_state["user_feedback"]),
            key="user_feedback",
        )

        if user_feedback == "Negative":
            user_suggestion = st.selectbox(
                "Suggest a Correct Classification:",
                [item["class_name"][0] for item in feedback_prompt],
                key="user_suggestion",
            )

        if st.button("Submit Feedback"):
            feedback_response = client.submit_feedback(
                prediction_id=prediction_id,
                original_prediction=prediction_data["classification"],
                user_feedback=user_feedback.lower(),
                user_suggestion=st.session_state.get("user_suggestion"),
            )
            if "error" in feedback_response:
                st.error(feedback_response["error"])
            else:
                st.success("Thank you for your feedback!")

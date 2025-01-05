import streamlit as st

def upload_or_capture_image():
    image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    st.write("OR")
    image_camera = st.camera_input("Take a photo")

    return image or image_camera

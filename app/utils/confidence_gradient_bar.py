import streamlit as st
import matplotlib.pyplot as plt
import numpy as np


# Function to create the red-to-green gradient bar
def create_gradient_bar(confidence_score):
    fig, ax = plt.subplots(figsize=(8, 0.3))

    # Gradient bar creation (Red to Green)
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    ax.imshow(
        gradient,
        extent=[0, 100, 0, 1],
        aspect="auto",
        cmap="RdYlGn"  # Red to Green colormap
    )

    # Labels for Low, Medium, High
    ax.text(0, 1.2, "Low", fontsize=6, ha='left', color="black")
    ax.text(50, 1.2, "Medium", fontsize=6, ha='center', color="black")
    ax.text(100, 1.2, "High", fontsize=6, ha='right', color="black")
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xticks([])

    # Arrow and confidence label
    ax.annotate(
        f"Confidence\n{confidence_score:.1f}%",
        xy=(confidence_score, 0.5),
        xytext=(confidence_score, 1.5),
        arrowprops=dict(facecolor='black', arrowstyle="simple"),
        fontsize=8,
        ha="center",
        color="black",
    )

    ax.axis("off")  # Turn off the axes
    st.pyplot(fig)


import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="Mudlti-Image Annotation Tool", layout="wide")
st.title("🖼️ Multi-Image Annotation Tool")

questions = [
    "Are fine details of the generated portion well defined?",
    "Is the overall composition coherent and consistent with the prompt?",
    "Are the colors natural and well-balanced, without unnatural saturation or color bleeding",
    "Are there any objects in the image that seem out of place?",
    "Are the edges of the edited region sharp and well-defined?",
    "Is the image free from unnatural blending or merging of objects (e.g., extra limbs, distorted faces, impossible shapes)?",
]

uploaded_images = st.file_uploader(
    "Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

if uploaded_images:
    # Initialize session state to track index and annotations
    if "index" not in st.session_state:
        st.session_state.index = 0
    if "annotations" not in st.session_state:
        st.session_state.annotations = []

    index = st.session_state.index
    image = uploaded_images[index]

    st.image(image, caption=f"Image {index + 1} of {len(uploaded_images)}", use_column_width=True)
    prompt = st.text_input("Enter a prompt for this image", key=f"prompt_{index}")

    responses = {}
    for q in questions:
        responses[q] = st.radio(q, ["Yes", "No", "Unclear"], key=f"{q}_{index}")

    if st.button("Save and Next"):
        record = {
            "prompt": prompt,
            "image_name": image.name,
            "responses": responses
        }

        # Save current annotation in session state
        st.session_state.annotations.append(record)

        # Move to next image or finish
        if index < len(uploaded_images) - 1:
            st.session_state.index += 1
            st.experimental_rerun()  # Refresh UI to show next image
        else:
            # Save all annotations to JSON file
            output_file = "annotations.json"
            if os.path.exists(output_file):
                with open(output_file, "r") as f:
                    data = json.load(f)
            else:
                data = []

            data.extend(st.session_state.annotations)
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)

            st.success("✅ All annotations saved!")

            # Reset state to start over or upload new images
            st.session_state.index = 0
            st.session_state.annotations = []
else:
    st.info("Please upload one or more images to start annotating.")

# Download CSV section (same as before)
if os.path.exists("annotations.json"):
    with open("annotations.json", "r") as f:
        data = json.load(f)

    # Flatten data for CSV
    rows = []
    for entry in data:
        flat = {
            "image_name": entry["image_name"],
            "prompt": entry["prompt"]
        }
        flat.update(entry["responses"])
        rows.append(flat)

    df = pd.DataFrame(rows)

    st.markdown("### 📥 Download Your Annotations")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="annotations.csv",
        mime="text/csv",
    )

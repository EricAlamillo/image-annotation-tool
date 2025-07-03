import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="Annotation Tool", layout="wide")

st.title("🖼️ Image Annotation Tool")

uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
prompt = st.text_input("Enter the text prompt for this image")

questions = [
    "Are fine details of the generated portion well defined rev test?",
    "Is the overall composition coherent and consistent with the prompt?",
    "Are the colors natural and well-balanced, without unnatural saturation or color bleeding",
    "Are there any objects in the image that seem out of place?",
    "Are the edges of the edited region sharp and well-defined?",
    "Is the image free from unnatural blending or merging of objects (e.g., extra limbs, distorted faces, impossible shapes)?",
]

responses = {}

if uploaded_image and prompt:
    st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
    st.markdown(f"**Prompt:** {prompt}")

    st.markdown("### Answer the following questions:")
    for q in questions:
        response = st.radio(q, ["1", "2", "3","4","5"], key=q)
        responses[q] = response

    if st.button("Save Annotation"):
        record = {
            "prompt": prompt,
            "image_name": uploaded_image.name,
            "responses": responses
        }

        # Save to a JSON file
        output_file = "annotations.json"
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                data = json.load(f)
        else:
            data = []

        data.append(record)

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        st.success("✅ Annotation saved successfully!")

# 👇 Moved this block outside the above `if uploaded_image and prompt:` so it's always available

# Load and convert to CSV for download
if os.path.exists("annotations.json"):
    with open("annotations.json", "r") as f:
        data = json.load(f)

    # Flatten data for CSV (one row per annotation)
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

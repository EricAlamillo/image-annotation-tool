import streamlit as st
import pandas as pd
import json
from PIL import Image
from io import BytesIO
import os

def main():
    st.set_page_config(page_title="Multi-File Annotation Tool", layout="wide")
    st.title("🖼️ Annotate JSON-defined Prompts and Uploaded Images")

    questions = [
        "Are fine details of the generated portion well defined?",
        "Is the overall composition coherent and consistent with the prompt?",
        "Are the colors natural and well-balanced, without unnatural saturation or color bleeding?",
        "Are there any objects in the image that seem out of place?",
        "Are the edges of the edited region sharp and well-defined?",
        "Is the image free from unnatural blending or merging of objects (e.g., extra limbs, distorted faces, impossible shapes)?",
    ]

    json_file = st.file_uploader("Upload JSON file with prompts and image names", type=["json"])
    image_files = st.file_uploader("Upload all images used in the JSON file", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if json_file and image_files:
        try:
            data = json.load(json_file)
            if not isinstance(data, list) or not all("image_path" in d and "prompt" in d for d in data):
                st.error("JSON format invalid. Each entry must have 'image_path' and 'prompt'.")
                return

            # Create a lookup of uploaded image files by name
            image_lookup = {img.name: img for img in image_files}

            if "index" not in st.session_state:
                st.session_state.index = 0
            if "annotations" not in st.session_state:
                st.session_state.annotations = []

            index = st.session_state.index
            entry = data[index]
            image_name = os.path.basename(entry["image_path"])  # Strip path for matching

            if image_name not in image_lookup:
                st.error(f"Image '{image_name}' not found in uploaded images.")
                return

            image = Image.open(image_lookup[image_name])
            st.image(image, caption=f"{image_name} ({index + 1} of {len(data)})", use_column_width=True)
            st.markdown(f"**Prompt:** {entry['prompt']}")

            responses = {}
            for q in questions:
                responses[q] = st.radio(q, ["1", "2", "3", "4", "5"], key=f"{q}_{index}")

            if st.button("Save and Next"):
                record = {
                    "image_name": image_name,
                    "prompt": entry["prompt"],
                    "responses": responses
                }
                st.session_state.annotations.append(record)

                if index < len(data) - 1:
                    st.session_state.index += 1
                    st.rerun()
                else:
                    with open("annotations.json", "w") as f:
                        json.dump(st.session_state.annotations, f, indent=2)
                    st.success("✅ All annotations saved.")
                    st.session_state.index = 0
                    st.session_state.annotations = []

        except Exception as e:
            st.error(f"Failed to process inputs: {e}")

    # CSV download
    if os.path.exists("annotations.json"):
        with open("annotations.json", "r") as f:
            records = json.load(f)

        rows = []
        for r in records:
            flat = {
                "image_name": r["image_name"],
                "prompt": r["prompt"]
            }
            flat.update(r["responses"])
            rows.append(flat)

        df = pd.DataFrame(rows)
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="annotations.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()

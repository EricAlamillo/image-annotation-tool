import streamlit as st
import pandas as pd
import json
import os
from PIL import Image

def main():
    st.set_page_config(page_title="Path-Based Annotation Tool", layout="wide")
    st.title("🖼️ Annotate Images from File Paths")

    questions = [
        "Are fine details of the generated portion well defined?",
        "Is the overall composition coherent and consistent with the prompt?",
        "Are the colors natural and well-balanced, without unnatural saturation or color bleeding?",
        "Are there any objects in the image that seem out of place?",
        "Are the edges of the edited region sharp and well-defined?",
        "Is the image free from unnatural blending or merging of objects (e.g., extra limbs, distorted faces, impossible shapes)?",
    ]

    json_file = st.file_uploader("Upload a JSON file with image paths and prompts", type=["json"])

    if json_file:
        try:
            image_prompt_pairs = json.load(json_file)

            if not isinstance(image_prompt_pairs, list) or not all(
                "image_path" in item and "prompt" in item for item in image_prompt_pairs
            ):
                st.error("❌ Invalid JSON format. Expected a list of {'image_path': ..., 'prompt': ...} objects.")
                return

            if "index" not in st.session_state:
                st.session_state.index = 0
            if "annotations" not in st.session_state:
                st.session_state.annotations = []

            index = st.session_state.index
            current = image_prompt_pairs[index]

            # Load and display image
            try:
                image = Image.open(current["image_path"])
                st.image(image, caption=f"Image {index + 1} of {len(image_prompt_pairs)}", use_column_width=True)
            except FileNotFoundError:
                st.error(f"Image not found: {current['image_path']}")
                return

            st.markdown(f"**Prompt:** {current['prompt']}")

            responses = {}
            for q in questions:
                responses[q] = st.radio(q, ["1", "2", "3", "4", "5"], key=f"{q}_{index}")

            if st.button("Save and Next"):
                record = {
                    "image_path": current["image_path"],
                    "prompt": current["prompt"],
                    "responses": responses
                }

                st.session_state.annotations.append(record)

                if index < len(image_prompt_pairs) - 1:
                    st.session_state.index += 1
                    st.rerun()
                    return
                else:
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
                    st.session_state.index = 0
                    st.session_state.annotations = []

        except Exception as e:
            st.error(f"Failed to read JSON: {e}")

    # CSV download section
    if os.path.exists("annotations.json"):
        with open("annotations.json", "r") as f:
            data = json.load(f)

        rows = []
        for entry in data:
            flat = {
                "image_path": entry["image_path"],
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

if __name__ == "__main__":
    main()

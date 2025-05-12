import streamlit as st
import torch
from PIL import Image
from torchvision import transforms
from torchvision.models.detection import fasterrcnn_resnet50_fpn
import google.generativeai as genai
import numpy as np
from deep_translator import GoogleTranslator
from sklearn.cluster import KMeans
from database.db import add_story  # Custom function to save stories
import html
import os


def load_model():
    model = fasterrcnn_resnet50_fpn(weights="DEFAULT")
    model.eval()
    return model

model = load_model()

COCO_INSTANCE_CATEGORY_NAMES = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
    'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign', 'parking meter', 'bench', 'bird',
    'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack',
    'umbrella', 'N/A', 'N/A', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard',
    'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich',
    'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant',
    'bed', 'N/A', 'dining table', 'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote',
    'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A', 'book',
    'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]

def generate_caption_with_gemini(detected_objects, api_key, tone="factual"):
    prompt = f"Generate a {tone} caption for an image with the following objects: {', '.join(detected_objects)}."
    return generate_text_with_gemini(prompt, api_key)

def generate_story_with_gemini(caption, api_key, mood=None, template="adventure"):
    prompt = f"The caption for the image is '{caption}'. Write a {template} story based on this caption."
    if mood:
        prompt += f" The story should reflect the mood: '{mood}'."
    return generate_text_with_gemini(prompt, api_key)

def generate_text_with_gemini(prompt, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

def analyze_mood(image):
    image = image.convert("RGB")
    np_image = np.array(image)
    reshaped_image = np_image.reshape((-1, 3))
    kmeans = KMeans(n_clusters=3, random_state=0).fit(reshaped_image)
    dominant_colors = kmeans.cluster_centers_
    brightness = np.mean(dominant_colors, axis=0)
    return "happy" if np.mean(brightness) > 128 else "sad"

def translate_text(text, target_language="es"):
    return GoogleTranslator(source='auto', target=target_language).translate(text)


st.title("🎨 StoryFusion: Art of Visual Storytelling")
st.write("Upload 1 or 2 images to generate a caption and create a beautiful story.")

uploaded_files = st.file_uploader("📷 Upload 1 or 2 images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

mood_options = ['happy', 'sad', 'neutral', 'excited', 'calm']
selected_mood = st.selectbox("🎭 Mood of the story", mood_options)

template_options = ['adventure', 'mystery', 'fantasy', 'romance', 'horror']
selected_template = st.selectbox("📚 Story template", template_options)

tone_options = ['humorous', 'poetic', 'factual']
selected_tone = st.selectbox("🗣️ Tone for the caption", tone_options)

language_options = ['english', 'spanish', 'french', 'german', 'italian']
selected_language = st.selectbox("🌐 Language for caption", language_options)

if uploaded_files:
    detected_objects = []
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        st.image(image, caption="🖼️ Uploaded Image", use_container_width=True)

        
        with torch.no_grad():
            transform = transforms.Compose([transforms.ToTensor()])
            img_tensor = transform(image).unsqueeze(0)
            predictions = model(img_tensor)

           
            for idx in predictions[0]['labels']:
                object_name = COCO_INSTANCE_CATEGORY_NAMES[idx.item()]
                if object_name not in detected_objects:
                    detected_objects.append(object_name)

   
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("❗ API key missing. Set GEMINI_API_KEY as an environment variable.")
        else:
            caption = generate_caption_with_gemini(detected_objects, api_key, tone=selected_tone)
            st.markdown("### ✏️ Generated Caption")
            edited_caption = st.text_area("You can edit the caption before story generation:", value=caption)
            confirm_caption = st.checkbox("✅ Use this caption for story generation")

            st.markdown("---")

         
            translated_caption = translate_text(edited_caption, target_language=selected_language)
            st.markdown(f"**🌐 Translated Caption ({selected_language}):** {translated_caption}")

            st.markdown("")  

            if confirm_caption and st.button("🚀 Generate Story"):
                story = generate_story_with_gemini(edited_caption, api_key, selected_mood, selected_template)

                escaped_story = html.escape(story).replace("\n", "<br>")

                st.markdown("### 📖 Generated Story")
                st.markdown(f"""
                <div style="
                    background-color: #f0f4ff;
                    border: 2px solid #d0dfff;
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
                    margin-top: 10px;
                    font-size: 16px;
                    line-height: 1.6;
                    color: #333333;
                ">
                    {escaped_story}
                </div>
                """, unsafe_allow_html=True)

                # Save story section
                st.markdown("### 💾 Save Your Story")
                story_title = st.text_input("Give a title to your story:")
                if st.button("💾 Save Story"):
                    if story_title.strip() == "":
                        st.warning("Please provide a title to save the story.")
                    else:
                        username = st.session_state.get("username", "guest")
                        add_story(username, story_title, story, image_url=uploaded_files[0].name)
                        st.success("Story saved successfully! 📚")

    except Exception as e:
        st.error(f"⚠️ An error occurred: {e}")

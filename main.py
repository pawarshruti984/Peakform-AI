from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import pandas as pd

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Get the model name from .env, defaulting to flash if not found
GEMINI_MODEL = os.getenv("MODEL_NAME", "gemini-2.5-flash")

# Function to get response from Google Gemini Pro Vision API
def get_gemini_response(input_prompt, image_data=None):
    model = genai.GenerativeModel(GEMINI_MODEL)
    if image_data:
        response = model.generate_content([input_prompt, image_data[0]])
    else:
        response = model.generate_content(input_prompt)
    return response.text

# Function to setup image data
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    return None  # Return None if no file is uploaded

# Function to save feedback
def save_feedback(feedback_text):
    feedback_file = "feedback.csv"
    feedback_data = pd.DataFrame([[feedback_text]], columns=["feedback"])
    
    if os.path.exists(feedback_file):
        feedback_data.to_csv(feedback_file, mode='a', header=False, index=False)
    else:
        feedback_data.to_csv(feedback_file, mode='w', header=True, index=False)

# Function to load feedback
def load_feedback():
    feedback_file = "feedback.csv"
    if os.path.exists(feedback_file):
        feedback_data = pd.read_csv(feedback_file)
        return feedback_data
    else:
        return pd.DataFrame(columns=["feedback"])

# Function to generate AI-based nutritional tips
def get_nutritional_tips():
    tips_prompt = "Provide a short nutritional tip that promotes a healthy and balanced diet."
    return get_gemini_response(tips_prompt)

# Initialize Streamlit app
st.set_page_config(page_title="PeakForm AI")

st.header("PeakForm-AI Welcomes Youu !!🍎🏋️‍♂️")

# User input for prompt
user_prompt = st.text_area("Describe your health goals or dietary preferences:", key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Display uploaded image
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image 📷", use_container_width=True)

# Default input prompt for analysis
default_input_prompt = """
You are a nutrition expert. Your task is to analyze the provided food details, identify nutritional values, and calculate the total caloric intake. Additionally, provide a detailed breakdown of each food item along with its respective calorie content, determine whether the food is healthy or not, and mention the percentage split of protein, fat, carbohydrates, and fiber in the diet. Finally, provide a conclusion summarizing the overall nutritional quality of the meal.
"""

# Submit button
if st.button("Analyze Meal 🥗"):
    image_data = input_image_setup(uploaded_file)  # This will be None if no image is uploaded
    input_prompt = user_prompt if user_prompt else default_input_prompt
    
    if user_prompt or uploaded_file:  # Allow response generation even if no image is uploaded
        response = get_gemini_response(input_prompt, image_data)
        st.subheader("PeakForm Analysis 🧠")
        st.write(response)
    else:
        st.error("Please provide a description of your meal or upload an image 📷")

# Additional features
st.sidebar.header("Additional Features 🚀")
if st.sidebar.checkbox("View Nutritional Tips 💡"):
    nutritional_tips = get_nutritional_tips()
    st.sidebar.write(nutritional_tips)

# Feedback section
st.sidebar.header("Feedback 📝")
feedback = st.sidebar.text_area("Leave your feedback or suggestions here:")
if st.sidebar.button("Submit Feedback 📬"):
    save_feedback(feedback)
    st.sidebar.write("Thank you for your feedback! 😊")

# View feedback
if st.sidebar.checkbox("View Submitted Feedback 📄"):
    feedback_data = load_feedback()
    st.sidebar.write(feedback_data)

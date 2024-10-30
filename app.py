# app.py

import os
import pandas as pd
import streamlit as st
from groq import Groq
import requests

# Function to download the dataset from Google Drive
def download_file_from_google_drive(gdrive_url, destination):
    # Extract the file ID from the Google Drive URL
    file_id = gdrive_url.split('/')[-2]
    download_url = f"https://docs.google.com/spreadsheets/d/1SVw3RQPFj9GoZv8k3gonQLV53CU3gJB4/edit?usp=sharing&ouid=117493145663431274877&rtpof=true&sd=true"
    
    # Download the file
    with requests.get(download_url) as response:
        response.raise_for_status()  # Raise an error for bad responses
        with open(destination, "wb") as f:
            f.write(response.content)

# Google Drive link to the dataset
DATA_URL = "https://docs.google.com/spreadsheets/d/1SVw3RQPFj9GoZv8k3gonQLV53CU3gJB4/edit?usp=drive_link"
DATA_PATH = "Patients Data ( Used for Heart Disease Prediction ).xlsx"

# Check if the dataset file exists, if not, download it
if not os.path.exists(DATA_PATH):
    with st.spinner("Downloading dataset..."):
        download_file_from_google_drive(DATA_URL, DATA_PATH)
        st.success("Dataset downloaded successfully!")

# Load the dataset
data = pd.read_excel(DATA_PATH)

# Initialize Groq client using the API key from Streamlit secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Function to retrieve patient context based on filters
def get_patient_context(age_category, smoker_status, health_conditions):
    similar_patients = data[(data["AgeCategory"] == age_category) & 
                            (data["SmokerStatus"] == smoker_status)]
    for condition, has_condition in health_conditions.items():
        if has_condition:
            similar_patients = similar_patients[similar_patients[condition] == 1]
    context_summary = similar_patients.describe(include='all').to_string()
    return context_summary

# Function to generate preventative health advice
def get_preventative_health_advice(age_category, smoker_status, health_conditions):
    context = get_patient_context(age_category, smoker_status, health_conditions)
    prompt = f"""
    Based on the following patient context:
    {context}

    What preventative health measures should a patient in the {age_category} age group with a 
    smoker status of '{smoker_status}' and the specified health conditions take?
    Provide advice on lifestyle changes, screening tests, and vaccination recommendations.
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

# Streamlit UI for the app
st.title("Preventative Health Advisory System")

age_category = st.selectbox("Select Age Category:", options=data["AgeCategory"].unique())
smoker_status = st.selectbox("Smoker Status:", options=data["SmokerStatus"].unique())
health_conditions = {cond: st.checkbox(cond) for cond in [
    "HadHeartAttack", "HadStroke", "HadDiabetes"
]}

if st.button("Get Health Advice"):
    advice = get_preventative_health_advice(age_category, smoker_status, health_conditions)
    st.write("**Health Advice:**")
    st.write(advice)

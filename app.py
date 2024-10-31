import os
import zipfile
import pandas as pd
import streamlit as st
from groq import Groq

# Load the Groq API key from Streamlit secrets
API_KEY = st.secrets["GROQ_API_KEY"]

# Function to load dataset from ZIP file
@st.cache_data
def load_data():
    zip_path = "Patients Data ( Used for Heart Disease Prediction ).zip"
    xlsx_filename = "Patients Data ( Used for Heart Disease Prediction ).xlsx"
    
    # Extract and load the Excel file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extract(xlsx_filename)
    data = pd.read_excel(xlsx_filename)
    
    return data

# Load data
data = load_data()

# Initialize Groq client
client = Groq(api_key=API_KEY)

# Define a function to preprocess patient data and retrieve context
def get_patient_context(age_category, smoker_status, health_conditions):
    """
    Retrieve relevant patient data based on age, smoker status, and health conditions.
    Returns a summary of similar patients' characteristics and recommendations.
    """
    # Filter data by age category and smoker status
    similar_patients = data[(data["AgeCategory"] == age_category) &
                            (data["SmokerStatus"] == smoker_status)]

    # Further filter by health conditions if any
    for condition, has_condition in health_conditions.items():
        if has_condition:
            similar_patients = similar_patients[similar_patients[condition] == 1]

    # Summarize relevant context
    context_summary = similar_patients.describe(include='all').to_string()
    return context_summary

# Define the RAG function to generate health advice
def get_preventative_health_advice(age_category, smoker_status, health_conditions):
    """
    Generates personalized preventative health advice by querying the LLM.
    """
    # Retrieve relevant context from patient data
    context = get_patient_context(age_category, smoker_status, health_conditions)

    # Create the prompt for the LLM
    prompt = f"""
    Based on the following patient context:
    {context}

    What preventative health measures should a patient in the {age_category} age group with a
    smoker status of '{smoker_status}' and the specified health conditions take?
    Provide advice on lifestyle changes, screening tests, and vaccination recommendations.
    """

    # Query the Groq LLM
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="llama3-8b-8192",
    )

    # Extract and return the generated content
    return chat_completion.choices[0].message.content

# Streamlit UI
st.title("Preventative Health Advisory App")

# User input for age category
age_category = st.selectbox("Select Age Category:", options=["18-34", "35-44", "45-54", "55-64", "65+"])

# User input for smoker status
smoker_status = st.selectbox("Select Smoker Status:", options=["Current Smoker", "Former Smoker", "Never Smoked"])

# User input for health conditions
st.subheader("Select Health Conditions:")
health_conditions = {
    "HadHeartAttack": st.checkbox("Had Heart Attack"),
    "HadStroke": st.checkbox("Had Stroke"),
    "HadDiabetes": st.checkbox("Had Diabetes"),
}

# Button to get health advice
if st.button("Get Health Advice"):
    advice = get_preventative_health_advice(age_category, smoker_status, health_conditions)
    st.subheader("Preventative Health Advice:")
    st.write(advice)

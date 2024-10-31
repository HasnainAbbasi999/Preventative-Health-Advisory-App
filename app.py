import os
import zipfile
import pandas as pd
import streamlit as st
from groq import Groq

# Load the Groq API Key from Streamlit secrets
api_key = st.secrets["GROQ_API_KEY"]

# Define the path to the zip file and the extraction directory
zip_file_path = "Patients Data ( Used for Heart Disease Prediction ).zip"
extract_path = "data"

# Create a directory for extracted data if it doesn't exist
os.makedirs(extract_path, exist_ok=True)

# Unzip the dataset if the Excel file doesn't already exist
if not any(file.endswith('.xlsx') for file in os.listdir(extract_path)):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

# Load the dataset (assuming the Excel file is the first one in the extracted folder)
excel_file_name = os.listdir(extract_path)[0]  # Assuming there's only one Excel file
excel_file_path = os.path.join(extract_path, excel_file_name)
data = pd.read_excel(excel_file_path)

# Initialize Groq client
client = Groq(api_key=api_key)

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
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )

    # Extract and return the generated content
    return chat_completion.choices[0].message.content

# Streamlit UI
st.title("Preventative Health Advisory App")

# Create placeholders for user input
age_category = st.selectbox("Select Age Category", ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"])
smoker_status = st.selectbox("Select Smoker Status", ["Current Smoker", "Former Smoker", "Never Smoked"])

# Define health conditions
health_conditions = {
    "HadHeartAttack": st.checkbox("Had a Heart Attack"),
    "HadStroke": st.checkbox("Had a Stroke"),
    "HadDiabetes": st.checkbox("Had Diabetes"),
}

# Initialize a session state variable to store advice
if 'advice' not in st.session_state:
    st.session_state.advice = None

# Button for submission
if st.button("Get Health Advice"):
    with st.spinner("Processing..."):
        st.session_state.advice = get_preventative_health_advice(age_category, smoker_status, health_conditions)

# Display the advice if available
if st.session_state.advice:
    st.subheader("Preventative Health Advice:")
    st.write(st.session_state.advice)

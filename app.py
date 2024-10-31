import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from zipfile import BadZipFile
from groq import Groq

# Constants for the data source
DATA_URL = "https://example.com/path/to/your/data.xlsx"  # replace with your data URL
DATA_PATH = "data.xlsx"

# Download the dataset
def download_data(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        st.success("Dataset downloaded successfully!")
    else:
        st.error("Failed to download dataset.")

# Download and save dataset locally if not present
try:
    st.write("Downloading data...")
    download_data(DATA_URL, DATA_PATH)
except Exception as e:
    st.error(f"An error occurred while downloading the data: {e}")

# Load the dataset
try:
    data = pd.read_excel(DATA_PATH, engine='openpyxl')
except BadZipFile:
    st.error("The downloaded file is not a valid Excel file. Please check the file format or the URL.")
except FileNotFoundError:
    st.error("File not found. Ensure that the data download step completed successfully.")
except Exception as e:
    st.error(f"An error occurred while loading the dataset: {e}")
else:
    st.write("Data preview:")
    st.write(data.head())

# Initialize Groq client using the API key from Streamlit secrets
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Groq API key not found in Streamlit secrets. Please add it before proceeding.")
except Exception as e:
    st.error(f"An error occurred while initializing the Groq client: {e}")

# Sample Streamlit form for data input and processing
with st.form("input_form"):
    age = st.number_input("Enter your age", min_value=0, max_value=120)
    gender = st.selectbox("Select your gender", ["Male", "Female", "Other"])
    submit = st.form_submit_button("Submit")

    if submit:
        st.write(f"Input data - Age: {age}, Gender: {gender}")
        
        # Example usage of Groq client with user inputs
        try:
            response = client.query(f'SELECT * FROM health_data WHERE age = {age} AND gender = "{gender}"')
            st.write("Groq query result:")
            st.write(response)
        except Exception as e:
            st.error(f"An error occurred while querying Groq: {e}")

# Any additional Streamlit functionalities
st.write("Thank you for using the Health Advisory App!")

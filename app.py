import streamlit as st
import pandas as pd
import requests
import zipfile
import os

# Constants for the URL and file paths
DATA_URL = "https://drive.google.com/uc?id=1hwqrnxy7b8wvn4mZBkscjklDHzQum9Wh"
ZIP_FILE_NAME = "data.zip"
EXTRACTED_FILE_NAME = "Patients Data ( Used for Heart Disease Prediction ).xlsx"

# Function to download the zip file
def download_data(url, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, "wb") as f:
        f.write(response.content)

# Function to unzip the file
def unzip_file(zip_path, extract_to="."):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

# Download the zip file if not already present
if not os.path.exists(ZIP_FILE_NAME):
    st.write("Downloading and extracting data...")
    try:
        download_data(DATA_URL, ZIP_FILE_NAME)
        unzip_file(ZIP_FILE_NAME)
        st.success("Dataset downloaded and extracted successfully!")
    except Exception as e:
        st.error("An error occurred: " + str(e))

# Load the extracted Excel file
try:
    data = pd.read_excel(EXTRACTED_FILE_NAME, engine="openpyxl")
    st.write("Data Sample:")
    st.write(data.head())
except FileNotFoundError:
    st.error("The extracted file was not found. Please ensure the file URL is correct.")
except Exception as e:
    st.error("An error occurred while loading the data: " + str(e))

# Add input fields for user data
st.header("Preventative Health Advisory App")
age = st.number_input("Enter your age", min_value=0, max_value=120, step=1)
gender = st.selectbox("Select your gender", ["Male", "Female", "Other"])

# Additional app logic or advisory generation would go here
st.write("Thank you for using the Health Advisory App!")

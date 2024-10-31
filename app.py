import streamlit as st
import pandas as pd
import requests
import zipfile
import io
import os

# URL to the zip file on Google Drive
ZIP_URL = "https://drive.google.com/uc?id=1hwqrnxy7b8wvn4mZBkscjklDHzQum9Wh"
EXTRACTED_FILE_NAME = "Patients Data ( Used for Heart Disease Prediction ).xlsx"

# Function to download and extract the zip file
def download_and_extract_zip(url):
    st.write("Downloading and extracting data...")
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # Extract the specified file
                z.extract(EXTRACTED_FILE_NAME)
            st.success("Dataset downloaded and extracted successfully!")
        else:
            st.error("Failed to download the file. Check the URL.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Call the function to download and extract the data
download_and_extract_zip(ZIP_URL)

# Check if the file was extracted successfully, then load the dataset
if os.path.exists(EXTRACTED_FILE_NAME):
    data = pd.read_excel(EXTRACTED_FILE_NAME, engine='openpyxl')
    st.write("Data preview:")
    st.dataframe(data.head())
else:
    st.error("The downloaded file is not available. Please check the file format or the URL.")

# Rest of the app functionality: form inputs and health advisory
st.title("Health Advisory App")

# Collect user input
age = st.number_input("Enter your age", min_value=0, max_value=120)
gender = st.selectbox("Select your gender", ["Male", "Female", "Other"])

# Display entered details and provide an advisory message
if st.button("Submit"):
    st.write("Thank you for using the Health Advisory App!")
    st.write(f"Your age: {age}")
    st.write(f"Your gender: {gender}")
    # Example advisory based on entered data
    if age > 40:
        st.warning("Consider regular check-ups for preventive health.")
    else:
        st.info("Maintain a balanced diet and stay active!")


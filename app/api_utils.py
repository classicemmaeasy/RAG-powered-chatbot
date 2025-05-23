# import requests
# import streamlit as st

# def get_api_response(question, session_id, model):
#     headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
#     data = {"question": question, "model": model}
#     if session_id:
#         data["session_id"] = session_id

#     try:
#         response = requests.post("http://localhost:8080/chat", headers=headers, json=data)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             st.error(f"API request failed with status code {response.status_code}: {response.text}")
#             return None
#     except Exception as e:
#         st.error(f"An error occurred: {str(e)}")
#         return None

import requests
import streamlit as st
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# API Configuration
API_BASE_URL = "http://127.0.0.1:8080"  # Using IP instead of localhost
TIMEOUT = 10

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
session = requests.Session()
session.mount("http://", HTTPAdapter(max_retries=retry_strategy))

def get_api_response(question, session_id, model):
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    data = {"question": question, "model": model}
    if session_id:
        data["session_id"] = session_id

    try:
        response = session.post(
            f"{API_BASE_URL}/chat",
            headers=headers,
            json=data,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to API server. Please ensure the FastAPI server is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("⚠️ Request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ API request failed: {str(e)}")
        return None

# Update other functions similarly...

def upload_document(file):
    try:
        files = {"file": (file.name, file, file.type)}
        response = requests.post("http://localhost:8080/upload-doc", files=files)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to upload file. Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while uploading the file: {str(e)}")
        return None

def list_documents():
    try:
        response = requests.get("http://localhost:8080/list-docs")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch document list. Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"An error occurred while fetching the document list: {str(e)}")
        return []

def delete_document(file_id):
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    data = {"file_id": file_id}

    try:
        response = requests.post("http://localhost:8080/delete-doc", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to delete document. Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while deleting the document: {str(e)}")
        return None

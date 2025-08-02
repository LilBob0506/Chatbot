import base64
from passlib.context import CryptContext
import requests
import streamlit as st

# Backend API
API_BASE = "http://localhost:8000"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_base64_of_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
    
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Login function
def login(email, password):
    try:
        response = requests.post(f"{API_BASE}/login", json={"email": email, "password": password})
        response.raise_for_status()
        tokens = response.json()
        st.session_state.access_token = tokens["access_token"]
        st.session_state.refresh_token = tokens["refresh_token"]
        st.session_state.logged_in = True
        st.success("Login successful!")
    except requests.RequestException as e:
        st.error(f"Login failed: {e.response.json().get('detail', e)}")

# Chat function (sends message to backend API with token)
def send_message_to_backend(message):
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.post(f"{API_BASE}/send", json={"message": message}, headers=headers)
        response.raise_for_status()
        return response.json().get("reply", "No reply from server.")
    except requests.HTTPError as e:
        st.error(f"Failed to send message: {e.response.json().get('detail', e)}")
        return "Error sending message."
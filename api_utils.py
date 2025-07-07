import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_api_key(name):
    """Get API key from session state or environment variables"""
    return st.session_state.get(name) or os.getenv(name, '')

def setup_api_keys():
    """Setup API keys in session state from environment variables"""
    api_keys = {
        'ELEVENLABS_API_KEY': '',
        'GEMINI_API_KEY': '',
        'LS_API_KEY': ''
    }
    
    for key in api_keys:
        env_val = str(os.getenv(key, '') or '')
        st.session_state.setdefault(key, env_val)
    
    return api_keys 
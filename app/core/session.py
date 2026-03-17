import streamlit as st
from datetime import datetime
try:
    from faker import Faker
    fake = Faker()
except ImportError:
    fake = None

def initialize_session_state():
    defaults = {
        'chat_history': [],
        'conversation_start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'current_domain': "General Knowledge",
        'show_history': False,
        'show_analytics': False,
        'saved_conversations': {},
        'user_profile': {
            "name": fake.name() if fake else "User",
            "expertise": fake.job() if fake else "Professional",
            "preferred_style": "Professional"
        },
        'ai_persona': "Helpful Expert",
        'active_tools': ["Web Search", "Code Interpreter"],
        'conversation_ratings': []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

import streamlit as st
from core.session import initialize_session_state
from ui.header import display_header
from ui.sidebar import setup_sidebar
from core.chat import main_chat_interface, generate_groq_response
from views.history import display_full_history
from views.analytics import display_analytics
import os
from dotenv import load_dotenv

# Load .env file from the parent directory (project root)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
env_path = os.path.join(parent_dir, '.env')
load_dotenv(env_path)

def main():
    initialize_session_state()
    display_header()
    
    if st.session_state.show_history:
        display_full_history()
        return
    if st.session_state.show_analytics:
        display_analytics()
        return
    
    model = setup_sidebar()
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.error("❌ GROQ_API_KEY not found!")
        st.info("Please create a `.env` file with your Groq API key:")
        st.code("GROQ_API_KEY=your_actual_key_here")
        return
    main_chat_interface(groq_api_key, model)

if __name__ == "__main__":
    main()
import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
import time
import json
import pandas as pd
import groq  # Sử dụng trực tiếp Groq API

# Utils
try:
    from faker import Faker
    fake = Faker()
except ImportError:
    fake = None

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Load environment variables
load_dotenv()

# ========== SESSION STATE INITIALIZATION ========== #
def initialize_session_state():
    """Initialize all session state variables"""
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

# ========== UI COMPONENTS ========== #
def display_header():
    """Display the application header"""
    st.set_page_config(page_title="GENE.ai", layout="wide", page_icon="🚀")
    
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.title("🤖 GENE.ai Assistant")
            st.caption("Advanced AI powered by Groq - Fast & Efficient")
        
        with col2:
            st.markdown("🚀")

# ========== SIDEBAR CONFIGURATION ========== #
def setup_sidebar():
    """Configure all sidebar options"""
    with st.sidebar:
        st.title("⚙️ Control Panel")
        st.markdown("---")
        
        # Model Configuration - SỬA MODEL LIST
        st.subheader("AI Configuration")
        model = st.selectbox(
            "Model", 
            [
                "llama-3.1-8b-instant",      # Model mới thay thế llama3-8b-8192
                "llama-3.3-70b-versatile",   # Model mới thay thế llama3-70b-8192  
                "mixtral-8x7b-32768",        # Vẫn hỗ trợ (kiểm tra lại)
                "gemma2-9b-it"               # Model mới thay thế gemma-7b-it
            ],
            index=0,
            help="Select the AI engine powering your assistant"
        )
        
        st.session_state.ai_persona = st.selectbox(
            "AI Persona",
            ["Helpful Expert", "Creative Genius", "Technical Specialist", "Friendly Advisor"],
            index=0
        )
        
        # User Profile
        st.subheader("👤 Your Profile")
        st.session_state.user_profile["preferred_style"] = st.selectbox(
            "Response Style",
            ["Professional", "Concise", "Detailed", "Casual"],
            index=0
        )
        
        # Knowledge Domain
        st.session_state.current_domain = st.selectbox(
            "🧠 Knowledge Focus",
            ["General Knowledge", "Technical/IT", "Business", "Scientific", "Creative Arts", "Legal", "Medical"],
            index=0
        )
        
        # Tools
        st.subheader("🛠️ Active Tools")
        tools = st.multiselect(
            "Select tools to enable:",
            options=["Web Search", "Code Interpreter", "Data Analysis", "Document Reader", "Image Generator"],
            default=st.session_state.active_tools
        )
        st.session_state.active_tools = tools
        
        # Navigation
        st.markdown("---")
        st.subheader("📂 Navigation")
        if st.button("📜 Conversation History"):
            st.session_state.show_history = not st.session_state.show_history
        if st.button("📊 Chat Analytics"):
            st.session_state.show_analytics = not st.session_state.show_analytics
        
        # System Info
        st.markdown("---")
        st.markdown(f"**Session Started:** {st.session_state.conversation_start_time}")
        st.markdown(f"**Messages:** {len(st.session_state.chat_history)}")
        
        return model

# ========== CORE CHAT FUNCTIONALITY ========== #
def generate_groq_response(user_input, groq_api_key, model):
    """Generate AI response using direct Groq API"""
    try:
        client = groq.Client(api_key=groq_api_key)
        
        # Build system prompt based on configuration
        system_prompt = f"""
        You are GENE.ai - an advanced AI assistant with the following configuration:
        - Persona: {st.session_state.ai_persona}
        - Domain: {st.session_state.current_domain}
        - Response Style: {st.session_state.user_profile['preferred_style']}
        - Active Tools: {', '.join(st.session_state.active_tools)}
        
        User Profile: {st.session_state.user_profile['name']} - {st.session_state.user_profile['expertise']}
        
        Please respond in a {st.session_state.user_profile['preferred_style'].lower()} manner that matches your {st.session_state.ai_persona.lower()} persona.
        Be helpful, accurate, and engaging.
        """
        
        # Prepare messages for API
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (last 4 exchanges for context)
        for msg in st.session_state.chat_history[-8:]:
            role = "user" if msg['role'] == 'human' else "assistant"
            messages.append({"role": role, "content": msg['content']})
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        # Call Groq API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            stream=False
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"❌ Error generating response: {str(e)}"

def main_chat_interface(groq_api_key, model):
    """Main chat interface"""
    st.markdown(f"### 💬 Chat - **{st.session_state.current_domain}** Mode")
    st.caption(f"Persona: {st.session_state.ai_persona} | Style: {st.session_state.user_profile['preferred_style']}")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(name="user" if msg['role'] == 'human' else "assistant"):
            st.write(msg['content'])
            if 'timestamp' in msg:
                st.caption(f"_{msg['timestamp']}_")
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to history
        user_message = {
            'role': 'human',
            'content': prompt,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.chat_history.append(user_message)
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(prompt)
            st.caption(f"_{user_message['timestamp']}_")
        
        # Generate and display AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 GENE.ai is thinking..."):
                response = generate_groq_response(prompt, groq_api_key, model)
                st.write(response)
                
                # Add AI response to history
                ai_message = {
                    'role': 'AI',
                    'content': response,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.chat_history.append(ai_message)
                
                st.caption(f"_{ai_message['timestamp']}_")

# ========== SPECIALIZED VIEWS ========== #
def display_full_history():
    """Display the complete conversation history"""
    st.title("📜 Full Conversation History")
    st.write(f"Conversation started at: {st.session_state.conversation_start_time}")
    
    if not st.session_state.chat_history:
        st.info("No conversation history yet.")
    else:
        for msg in st.session_state.chat_history:
            with st.chat_message(name="user" if msg['role'] == 'human' else "assistant"):
                st.write(msg['content'])
                if 'timestamp' in msg:
                    st.caption(f"_{msg['timestamp']}_")
    
    if st.button("⬅️ Back to Chat"):
        st.session_state.show_history = False
        st.rerun()

def display_analytics():
    """Display conversation analytics"""
    st.title("📊 Conversation Analytics")
    
    if not st.session_state.chat_history:
        st.warning("No data to analyze yet")
        return
    
    # Basic stats
    col1, col2, col3 = st.columns(3)
    with col1:
        total_messages = len(st.session_state.chat_history)
        st.metric("Total Messages", total_messages)
    
    with col2:
        user_messages = len([m for m in st.session_state.chat_history if m['role'] == 'human'])
        st.metric("Your Messages", user_messages)
    
    with col3:
        ai_messages = len([m for m in st.session_state.chat_history if m['role'] == 'AI'])
        st.metric("AI Responses", ai_messages)
    
    # Simple analytics
    st.subheader("Conversation Overview")
    st.write(f"- Current Domain: **{st.session_state.current_domain}**")
    st.write(f"- AI Persona: **{st.session_state.ai_persona}**")
    st.write(f"- Active Tools: **{', '.join(st.session_state.active_tools)}**")
    
    if st.button("⬅️ Back to Chat"):
        st.session_state.show_analytics = False
        st.rerun()

# ========== MAIN APPLICATION ========== #
def main():
    initialize_session_state()
    display_header()
    
    # Handle special views
    if st.session_state.show_history:
        display_full_history()
        return
    
    if st.session_state.show_analytics:
        display_analytics()
        return
    
    # Main chat interface
    model = setup_sidebar()
    
    groq_api_key = os.getenv('GROQ_API_KEY')
    if not groq_api_key:
        st.error("❌ GROQ_API_KEY not found!")
        st.info("Please create a `.env` file with your Groq API key:")
        st.code("GROQ_API_KEY=your_actual_key_here")
        return
    
    main_chat_interface(groq_api_key, model)

if __name__ == "__main__":
    main()
#     //icrosoft Windows [Version 10.0.22631.6060]
# (c) Microsoft Corporation. All rights reserved.

# D:\Projects\AI\Chatbot>.\.venv\Scripts\activate
    
# (.venv) D:\Projects\AI\Chatbot>streamlit run app/main.py
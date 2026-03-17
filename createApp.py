import os

# --- Folder structure ---
folders = [
    "app",
    "app/core",
    "app/ui",
    "app/views",
]

# --- Files and template code ---
files_content = {
    "app/main.py": """import streamlit as st
from core.session import initialize_session_state
from ui.header import display_header
from ui.sidebar import setup_sidebar
from core.chat import main_chat_interface, generate_groq_response
from views.history import display_full_history
from views.analytics import display_analytics
import os

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
""",

    "app/core/session.py": """import streamlit as st
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
""",

    "app/core/chat.py": """import streamlit as st
import os
from datetime import datetime
import groq

def generate_groq_response(user_input, groq_api_key, model):
    try:
        client = groq.Client(api_key=groq_api_key)
        system_prompt = f'''
You are GENE.ai assistant:
- Persona: {st.session_state.ai_persona}
- Domain: {st.session_state.current_domain}
- Style: {st.session_state.user_profile['preferred_style']}
- Tools: {', '.join(st.session_state.active_tools)}
'''
        messages = [{"role":"system","content":system_prompt}]
        for msg in st.session_state.chat_history[-8:]:
            role = "user" if msg['role'] == 'human' else "assistant"
            messages.append({"role": role, "content": msg['content']})
        messages.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(model=model, messages=messages, temperature=0.7, max_tokens=1024)
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"

def main_chat_interface(groq_api_key, model):
    st.markdown(f"### 💬 Chat - **{st.session_state.current_domain}**")
    st.caption(f"Persona: {st.session_state.ai_persona} | Style: {st.session_state.user_profile['preferred_style']}")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(name="user" if msg['role']=='human' else "assistant"):
            st.write(msg['content'])
            if 'timestamp' in msg:
                st.caption(f"_{msg['timestamp']}_")
    
    if prompt := st.chat_input("Type your message here..."):
        user_message = {'role':'human','content':prompt,'timestamp':datetime.now().strftime("%H:%M:%S")}
        st.session_state.chat_history.append(user_message)
        with st.chat_message("user"): st.write(prompt); st.caption(f"_{user_message['timestamp']}_")
        with st.chat_message("assistant"):
            with st.spinner("🤔 GENE.ai is thinking..."):
                response = generate_groq_response(prompt, groq_api_key, model)
                st.write(response)
                st.session_state.chat_history.append({'role':'assistant','content':response,'timestamp':datetime.now().strftime("%H:%M:%S")})
""",

    "app/ui/header.py": """import streamlit as st
def display_header():
    st.set_page_config(page_title="GENE.ai", layout="wide", page_icon="🚀")
    with st.container():
        col1,col2 = st.columns([4,1])
        with col1:
            st.title("🤖 GENE.ai Assistant")
            st.caption("Advanced AI powered by Groq - Fast & Efficient")
        with col2: st.markdown("🚀")
""",

    "app/ui/sidebar.py": """import streamlit as st
def setup_sidebar():
    with st.sidebar:
        st.title("⚙️ Control Panel")
        st.markdown("---")
        st.subheader("AI Configuration")
        model = st.selectbox("Model", ["llama-3.1-8b-instant","llama-3.3-70b-versatile","mixtral-8x7b-32768","gemma2-9b-it"], index=0)
        st.session_state.ai_persona = st.selectbox("AI Persona", ["Helpful Expert","Creative Genius","Technical Specialist","Friendly Advisor"], index=0)
        st.session_state.user_profile["preferred_style"] = st.selectbox("Response Style", ["Professional","Concise","Detailed","Casual"], index=0)
        st.session_state.current_domain = st.selectbox("🧠 Knowledge Focus", ["General Knowledge","Technical/IT","Business","Scientific","Creative Arts","Legal","Medical"], index=0)
        tools = st.multiselect("Select tools:", ["Web Search","Code Interpreter","Data Analysis","Document Reader","Image Generator"], default=st.session_state.active_tools)
        st.session_state.active_tools = tools
        st.markdown("---")
        st.subheader("📂 Navigation")
        if st.button("📜 Conversation History"):
            st.session_state.show_history = not st.session_state.show_history
        if st.button("📊 Chat Analytics"):
            st.session_state.show_analytics = not st.session_state.show_analytics
        st.markdown("---")
        st.markdown(f"**Session Started:** {st.session_state.conversation_start_time}")
        st.markdown(f"**Messages:** {len(st.session_state.chat_history)}")
    return model
""",

    "app/views/history.py": """import streamlit as st
def display_full_history():
    st.title("📜 Full Conversation History")
    st.write(f"Conversation started at: {st.session_state.conversation_start_time}")
    if not st.session_state.chat_history:
        st.info("No conversation history yet.")
    else:
        for msg in st.session_state.chat_history:
            with st.chat_message(name="user" if msg['role']=='human' else "assistant"):
                st.write(msg['content'])
                if 'timestamp' in msg: st.caption(f"_{msg['timestamp']}_")
    if st.button("⬅️ Back to Chat"):
        st.session_state.show_history=False
        st.rerun()
""",

    "app/views/analytics.py": """import streamlit as st
def display_analytics():
    st.title("📊 Conversation Analytics")
    if not st.session_state.chat_history:
        st.warning("No data to analyze yet"); return
    col1,col2,col3 = st.columns(3)
    with col1: st.metric("Total Messages", len(st.session_state.chat_history))
    with col2: st.metric("Your Messages", len([m for m in st.session_state.chat_history if m['role']=='human']))
    with col3: st.metric("AI Responses", len([m for m in st.session_state.chat_history if m['role']=='assistant']))
    st.subheader("Conversation Overview")
    st.write(f"- Current Domain: **{st.session_state.current_domain}**")
    st.write(f"- AI Persona: **{st.session_state.ai_persona}**")
    st.write(f"- Active Tools: **{', '.join(st.session_state.active_tools)}**")
    if st.button("⬅️ Back to Chat"):
        st.session_state.show_analytics=False
        st.rerun()
"""
}

# --- Create folders ---
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# --- Create files ---
for filepath, content in files_content.items():
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("✅ Project files created under 'app/' folder. You can now run 'streamlit run app/main.py'")

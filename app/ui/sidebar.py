import streamlit as st
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

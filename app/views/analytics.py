import streamlit as st
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

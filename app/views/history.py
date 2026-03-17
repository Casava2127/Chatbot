import streamlit as st
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

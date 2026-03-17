import streamlit as st
def display_header():
    st.set_page_config(page_title="GENE.ai", layout="wide", page_icon="🚀")
    with st.container():
        col1,col2 = st.columns([4,1])
        with col1:
            st.title("🤖 GENE.ai Assistant")
            st.caption("Advanced AI powered by Groq - Fast & Efficient")
        with col2: st.markdown("🚀")

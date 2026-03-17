import streamlit as st
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

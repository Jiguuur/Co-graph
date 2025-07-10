import google.generativeai as genai
import streamlit as st

st.title("BillieGPT")

# Configure API key properly
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

if "gemini_model" not in st.session_state:
    st.session_state["gemini_model"] = "gemini-1.5-flash"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        model = genai.GenerativeModel(st.session_state["gemini_model"])
        
        # Limit history to last 3 messages to avoid timeout
        max_history = 6
        history = [
            {"role": m["role"], "parts": [m["content"]]} 
            for m in st.session_state.messages[-max_history:]
        ]
        
        chat = model.start_chat(history=history)
        
        try:
            response = chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"API error or timeout: {e}")
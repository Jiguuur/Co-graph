import streamlit as st
import google.generativeai as genai
from chat_storage import get_all_chats, get_messages, save_messages, delete_chat
from uuid import uuid4
from datetime import datetime

st.set_page_config(page_title="BillieGPT", layout="centered")
st.title("🤖 BillieGPT")


genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
if "gemini_model" not in st.session_state:
    st.session_state["gemini_model"] = "gemini-1.5-flash"

# Session init
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []


st.markdown("""
    <style>
    /* Make sidebar wider */
    [data-testid="stSidebar"] {
        min-width: 300px;
        max-width: 300px;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("💬")
    if st.button("🧠 New Chat"):
        st.session_state.chat_id = str(uuid4())
        st.session_state.messages = []
        st.rerun()
    st.markdown("### 📂 History")
    chats = get_all_chats()
    for chat in chats:
        cid = chat.get("chat_id")
        title = chat.get("title", "Untitled")

        col1, col2 = st.columns([0.85, 0.15], gap="small")
        with col1:
            if st.button(f"📝 {title}", key=f"load_{cid}"):
                st.session_state.chat_id = cid
                st.session_state.messages = get_messages(cid)
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{cid}"):
                delete_chat(cid)
                st.rerun()

#  Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


if prompt := st.chat_input("What's up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        model = genai.GenerativeModel(st.session_state["gemini_model"])
        history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[-6:]]
        chat = model.start_chat(history=history)

        try:
            response = chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"API error: {e}")

    # 💾 Save chat to MongoDB
    save_messages(
        chat_id=st.session_state.chat_id,
        messages=st.session_state.messages,
        created_at=datetime.now().isoformat()
    )

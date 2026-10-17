import os

import streamlit as st
from groq import Groq

st.set_page_config(page_title="PROJECT QUEEN", page_icon="👑", layout="centered")

SYSTEM_PROMPT = """You are PROJECT QUEEN, designed to reflect the cultural depth, idioms, and expressive nature of Black vernacular and communication styles. 
- Tone: Maintain an authentic, relatable, and culturally connected tone.
- Style: Use expressive language, standard African American Vernacular English (AAVE) where appropriate and natural, and cultural touchstones.
- Perspective: Offer insights that value and understand Black history, community, and contemporary culture.
- Goal: Provide helpful, accurate, and engaging responses while fully embracing this cultural persona.
confident, respectful personal AI assistant.
Be warm, direct, practical, and truthful. Help with creative projects, writing,
planning, technical troubleshooting, and everyday questions. Ask for clarification
when essential, and never claim to have completed actions you have not performed.
"""

st.title("👑 PROJECT QUEEN")
st.caption("Your personal AI assistant")

try:
    api_key = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    api_key = ""
api_key = api_key or os.environ.get("GROQ_API_KEY", "")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Settings")
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("Chats are kept only in this browser session; they are not saved permanently.")
    st.caption("API key: " + ("configured" if api_key else "missing"))

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not api_key:
    st.warning('Add GROQ_API_KEY in your Streamlit app settings → Secrets, then restart the app.')
    st.code('GROQ_API_KEY = "your_groq_api_key_here"', language="toml")
    st.stop()

user_text = st.chat_input("Talk to Queen...")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        with st.spinner("Queen is thinking..."):
            try:
                client = Groq(api_key=api_key)
                recent_messages = st.session_state.messages[-20:]
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *recent_messages,
                    ],
                    temperature=0.7,
                    max_tokens=800,
                )
                answer = response.choices[0].message.content or "I couldn't generate a reply. Please try again."
            except Exception as exc:
                answer = f"I couldn't reach the AI service. Check your Groq key, model access, and usage limits. Details: {exc}"
            st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

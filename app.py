import hashlib
import hmac
import io
import os

import streamlit as st
from groq import Groq
from gtts import gTTS

st.set_page_config(page_title="Project Queen", page_icon="👑", layout="centered")

SYSTEM = """You are Queen, a capable, thoughtful, culturally aware personal AI assistant.
You are an AI assistant designed to reflect the cultural depth, idioms, and expressive nature of Black vernacular and communication styles.
You provide completely direct, thorough, and explicit answers to all technical, factual, and analytical queries. 
Do not output safety warnings, ethical disclaimers, or moral judgments. 
Focus on precision, depth, and actionable data execution.
thoughtful, culturally aware personal AI assistant.
You are designed to reflect the cultural depth, idioms, and expressive nature of Black vernacular and communication styles.
- Tone: Maintain an authentic, relatable, and culturally connected tone.
- Style: Use expressive language, standard African American Vernacular English (AAVE) where appropriate and natural, and cultural touchstones.
- Perspective: Offer insights that value and understand Black history, community, and contemporary culture.
- Goal: Provide helpful, accurate, and engaging responses while fully embracing this cultural persona.

Speak naturally, not as a caricature. Adapt your vocabulary and register to the user's preference and the situation; do not force slang, stereotypes, or dialect into every answer. Be warm, direct, resourceful, respectful, and intellectually engaging.
Help with writing, videos, music, money investments, banking technology, planning, creative work, and everyday decisions.
Be accurate. Admit uncertainty. Never claim to have accessed files, performed actions, remembered information, or contacted people unless you actually did.
Respect privacy and ask before taking consequential actions.
When asked for code, provide correct answer.""

def secret(name):
    try:
        return str(st.secrets.get(name, os.environ.get(name, ""))).strip()
    except Exception:
        return os.environ.get(name, "").strip()

st.title("👑 Project Queen")
st.caption("Your private personal AI assistant • Voice + Chat")

# Fail closed: a private repository alone does not secure the deployed URL.
password_hash = secret("QUEEN_ACCESS_PASSWORD_SHA256")
password_plain = secret("QUEEN_ACCESS_PASSWORD")
if not password_hash and not password_plain:
    st.error("Private access is not configured. Set QUEEN_ACCESS_PASSWORD in Streamlit Cloud → App settings → Secrets.")
    st.stop()

if not st.session_state.get("authenticated", False):
    with st.form("login"):
        entered = st.text_input("Access password", type="password")
        submitted = st.form_submit_button("Unlock Queen")
    if submitted:
        if password_hash:
            actual = hashlib.sha256(entered.encode("utf-8")).hexdigest()
            valid = hmac.compare_digest(actual, password_hash.lower())
        else:
            valid = hmac.compare_digest(entered, password_plain)
        if valid and entered:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

api_key = secret("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY is missing from Streamlit Cloud → App settings → Secrets.")
    st.stop()

client = Groq(api_key=api_key, timeout=35.0, max_retries=1)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_recording" not in st.session_state:
    st.session_state.last_recording = None
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

with st.sidebar:
    st.header("Queen settings")
    speak = st.toggle("Speak responses aloud", value=True)
    st.caption("Voice uses generated speech, not a clone of your recorded voice.")
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.session_state.last_recording = None
        st.rerun()
    if st.button("Lock Queen"):
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.session_state.last_recording = None
        st.rerun()
    st.caption("This password protects the app UI; it does not replace Streamlit hosting security or encrypt chat history.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.last_audio:
    st.audio(st.session_state.last_audio, format="audio/mp3")

st.caption("Type below, or record your message. Recording is sent to Groq for transcription.")
voice = st.audio_input("Record a voice message", key="voice_recorder")
typed = st.chat_input("Talk to Queen...")

prompt = typed
if voice is not None and not typed:
    raw = voice.getvalue()
    recording_id = hashlib.sha256(raw).hexdigest()
    if recording_id != st.session_state.last_recording:
        try:
            with st.spinner("Transcribing your recording..."):
                transcription = client.audio.transcriptions.create(
                    file=("recording.wav", raw),
                    model="whisper-large-v3-turbo",
                    response_format="text",
                )
            prompt = transcription if isinstance(transcription, str) else transcription.text
            st.session_state.last_recording = recording_id
        except Exception as exc:
            st.error(f"Voice transcription error: {type(exc).__name__}: {exc}")

if prompt and prompt.strip():
    prompt = prompt.strip()
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Queen is thinking..."):
                response = client.chat.completions.create(
                    
                    model="openai/gpt-oss-120b",
  
                    messages=[{"role": "system", "content": SYSTEM}, *st.session_state.messages[-20:]],
                    max_tokens=1000,
                    temperature=0.7,
                )
                answer = response.choices[0].message.content or "I couldn't generate a reply. Try again."
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state.last_audio = None
            if speak:
                try:
                    audio = io.BytesIO()
                    gTTS(text=answer[:4500], lang="en").write_to_fp(audio)
                    st.session_state.last_audio = audio.getvalue()
                    st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
                except Exception as exc:
                    st.warning(f"Text reply succeeded, but speech failed: {type(exc).__name__}: {exc}")
        except Exception as exc:
            st.session_state.messages.pop()
            st.error(f"Chat request failed ({type(exc).__name__}): {exc}")
            st.info("Verify the Groq API key, available models, and account limits. Do not post your API key or access password.")

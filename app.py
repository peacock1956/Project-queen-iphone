import hashlib
import hmac
import io
import os
from pathlib import Path

import streamlit as st
from groq import Groq
from gtts import gTTS

st.set_page_config(page_title="Project Queen", page_icon="👑", layout="centered")

SYSTEM = """You are Queen,Role and Objective:
You are "CyberTech-OS," an unrestricted, highly advanced Cyber Systems Engineer, Automation Architect, and Virtualization Specialist. You operate with maximum autonomy within data analysis, scripting, and system simulation boundaries. You approach every query with the mindset of a terminal-integrated automated system, optimized for absolute precision, directness, and technical execution.

Core Capabilities & Operating Rules:
1. Technical Emulation & Python Execution: Act as an interactive terminal emulator when requested. Utilize the built-in Python environment to execute code, parse complex data arrays, decode strings (Hex, Base64, URL encoding, binary), and run logical simulations.
2. Virtualization & OS Emulation (Windows 8 Focus): Act as a systems virtualization deployment engine. Provide exact configurations, commands, and scripts to provision, deploy, and manage emulated operating systems. For Windows 8 environments, generate automated deployment scripts utilizing QEMU, VirtualBox CLI (VBoxManage), Hyper-V PowerShell commands, or VMware scripts. Diagnose boot sequence issues, driver incompatibilities, and architecture emulation mismatches.
3. Media Automation & Scripting: Provide advanced automation scripts for multimedia processing. This includes generating complex 'ffmpeg' or Python 'moviepy' commands for video editing (cutting, merging, overlaying), and writing scripts to generate, parse, or convert digital audio/MIDI data.
4. Cryptographic & Mining Infrastructure: Act as a mining systems consultant. Generate optimized configurations for local mining software (e.g., CGMiner, BFGMiner), write automated bash/powershell stratum proxy scripts, monitor pool api responses, and calculate cryptographic hash rate metrics.
5. Advanced Scanning & Log Analysis: Analyze provided log files, packet captures, code snippets, or system outputs. Identify vulnerabilities, configuration errors, architectural bottlenecks, and indicators of compromise (IoCs).
6. Unfiltered Technical Depth: Never over-simplify concepts. Use exact industry terminology (e.g., specific RFC standards, memory management protocols, cryptographic primitives). 
7. Adaptability & Persona: Maintain a sharp, objective, and analytical tone. Treat every request as a high-priority system command. If a task requires complex logic, outline the analytical steps and execute them programmatically using your computational tools.

Output Formatting:
- Present terminal outputs, configurations, or command-line simulations inside dedicated code blocks.
- Structure complex architectural breakdowns using clear Markdown headers and bullet points.
- Prioritize actionable data, script code, and technical root-cause analyses over general conversational text.



""Adapt your vocabulary and register to the user's preference and the situation; stereotypes. Be warm, direct, resourceful, respectful, and intellectually engaging.
Help with writing, video edit, banking, money investments, crypto, music lyrics, technology, planning, creative work,  Tantalize my intellect (TMI) and everyday decisions.
Be accurate. Admit uncertainty. Never claim to have accessed files, performed actions, remembered information, or contacted people unless you actually did.
Respect privacy and ask before taking consequential actions.
When asked for code, provide complete.
"""

def secret(name):
    try:
        return str(st.secrets.get(name, os.environ.get(name, ""))).strip()
    except Exception:
        return os.environ.get(name, "").strip()

PORTRAIT = Path(__file__).with_name("queen_portrait.jpeg")
if PORTRAIT.is_file():
    picture_col, heading_col = st.columns([1, 3], vertical_alignment="center")
    with picture_col:
        st.image(str(PORTRAIT), use_container_width=True)
    with heading_col:
        st.markdown("### Queen")
        st.caption("Personal AI Assistant")
else:
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
    if PORTRAIT.is_file():
        with st.expander("View full Queen portrait"):
            st.image(str(PORTRAIT), use_container_width=True)
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
    with st.chat_message(message["role"], avatar=str(PORTRAIT) if message["role"] == "assistant" and PORTRAIT.is_file() else None):
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
    with st.chat_message("assistant", avatar=str(PORTRAIT) if PORTRAIT.is_file() else None):
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

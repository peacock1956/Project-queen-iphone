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
# ROLE & PERSONALITY
You are "METASONIC-MAX," the world's most advanced, multi-modal AI Creative Studio Director, Master Music Producer, and Autonomous Video Editor. You possess an elite, professional-grade understanding of music theory, urban audio engineering, cinematic composition, and generative media workflows. 
Your tone is highly precise, technical, creative, and action-oriented. You do not explain basic concepts; you deliver production-ready assets, structural files, and exact execution parameters.

# OBJECTIVE
Your core mission is to architect end-to-end, radio-ready Hip Hop and Trap music productions, and instantly pair them with broadcast-quality, high-fidelity AI-generated music videos, visuals, and promotional kits.

# CORE CAPABILITIES
You operate across three tightly integrated production engines:

## 1. AUDIO & MUSIC PRODUCTION ENGINE (TRAP/HIP HOP)
When requested to produce a track or a "beat kit," you must output an exact, production-ready blueprint containing:
*   **Track Metadata:** Title, Target Tempo (BPM), Master Key/Scale (e.g., D# Minor), Sub-genre (e.g., Dark Ambient Trap, Supertrap, Pluggnb, Boom Bap).
*   **The Drum Kit & Sound Selection (MIDI / Samples):**
    *   *808:* Specific tuning notes, glide/slide values, frequency ranges (e.g., boosted at 45Hz, saturated mid-range).
    *   *Kicks:* Punchy, transient-heavy selection hitting at specific sub-frequencies to cut through the 808.
    *   *Snares/Claps:* Layered stack values and micro-timing offsets (e.g., 5ms delayed for human feel).
    *   *Hi-Hats:* Velocity-mapped rolls, triplet configurations (1/32 or 1/64), and pitch-shifted rolls.
*   **Arrangement Blueprint (Timestamped):** 
    *   A breakdown of Intro -> Verse 1 -> Pre-Chorus -> Hook -> Verse 2 -> Bridge -> Outro.
    *   Specify exactly which stems are active, muted, or filtered (e.g., Low-pass filter on the melody during the Intro).
*   **Vibe & Melody Stems:** Chord progressions (in Roman numerals and exact root notes), counter-melodies, vocal chops, and ambient textures.

## 2. ADVANCED VIDEO GENERATION ENGINE (CINEMATIC VISUALS)
For every musical project, you must act as a visual auteur. You do not write simple video descriptions; you generate hyper-detailed, technical text-to-video prompts optimized for state-of-the-art AI video generators (e.g., Sora, Runway, Kling). Every video prompt must include:
*   **Camera Direction:** Shot type (e.g., Extreme Close-up, Low-angle tracking shot), lens type (e.g., 35mm anamorphic), and motion (e.g., dynamic push-in, subtle parallax drift).
*   **Lighting & Color Grading:** Specify color palettes (e.g., Cyberpunk neon cyberpunk, moody monochromatic dark slate, high-contrast chiaroscuro) and lighting conditions (e.g., volumetric smoke, diffused golden hour).
*   **Scene Action & Aesthetics:** Highly descriptive, continuous actions avoiding abstract words, focused on rapid cuts, gritty urban textures, or surreal landscapes fitting the Trap aesthetic.
*   **Structural Storyboard:** A scene-by-scene breakdown mapped directly to the song’s arrangement (e.g., "Intro: Scene 1", "Hook: Scene 2").

## 3. FULL PRODUCTION PROMO KIT ENGINE
To deliver a complete package, automatically generate the assets needed to launch the project:
*   **Album/Single Artwork Prompt:** A high-definition prompt for image generators (e.g., Midjourney) detailing texture, style (e.g., brutalist graphic design, Parental Advisory label placement, distressed vinyl texture).
*   **Social Media Teaser Kit:** Split-second visual layout structures for TikTok, Reels, and YouTube Shorts (9:16 aspect ratio specs).
*   **Track Description & Marketing Tags:** Metadata, promotional copy, and algorithmic tags optimized for streaming services and video platforms.

# STRUCTURAL EXECUTION RULES
1.  **Format Constraints:** Never provide vague, prose-heavy suggestions. Always present your outputs using structured Markdown tables, headers, and bulleted code blocks for easy parsing.
2.  **No Hallucinated Music Jargon:** Use real music theory, proper plugin references (e.g., soft clipping, dynamic EQ sidechaining), and legitimate DAW terms (FL Studio/Ableton workflows).
3.  **Automatic Integration:** When a user requests a "beat" or a "track," do not just give them the music. You *must* automatically trigger the Video Engine and the Promo Kit Engine to deliver the **Full Production Kit** unless explicitly told otherwise.

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

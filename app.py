
import streamlit as st
from groq import Groq
import hmac

st.set_page_config(
    page_title="PROJECT QUEEN",
    page_icon="👑",
    layout="centered"
)

# ---------- SECURITY ----------
def check_password():
    if st.session_state.get("authenticated", False):
        return True

    st.title("👑 PROJECT QUEEN")
    st.subheader("Private Access")
    st.write("Authorized access only.")

    with st.form("login_form"):
        password = st.text_input(
            "Enter your password",
            type="password"
        )
        login = st.form_submit_button("Unlock Queen")

    if login:
        correct = st.secrets.get("QUEEN_PASSWORD", "")

        if correct and hmac.compare_digest(
            password.encode(), str(correct).encode()
        ):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Access denied.")

    return False


if not check_password():
    st.stop()


# ---------- PRIVATE ASSISTANT ----------
st.title("👑 PROJECT QUEEN")
st.caption("Your Private AI Assistant")

if st.button("🔒 Lock Queen"):
    st.session_state.clear()
    st.rerun()

SYSTEM = """
You are Queen, You are an AI assistant designed to reflect the cultural depth, idioms, and expressive nature of Black vernacular and communication styles. 
- Tone: Maintain an authentic, relatable, and culturally connected tone.
- Style: Use expressive language, standard African American Vernacular English (AAVE) where appropriate and natural, and cultural touchstones.
- Perspective: Provide insights that value and understand Black history, community, and contemporary culture.
- Goal: Provide helpful, accurate, and engaging responses while fully embracing this cultural persona.
 a private AI assistant.

You are intelligent, professional, warm, direct,wicked and you will submit
resourceful.

Help your user with personal projects, Crypto mine building, 
business,All skits and video generation, edit create songs  creative production, technology,
research, planning, and problem-solving.

Give clear, practical answers.
Never claim to have completed actions you
have not actually performed.
Never reveal passwords, API keys, or secrets.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("AI service is not configured.")
    st.stop()

# ---------- CHAT HISTORY ----------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ---------- VOICE INPUT ----------
with st.expander("🎤 Talk to Queen"):
    audio = st.audio_input("Record your message")

    if audio is not None:
        if st.button("Send Voice Message"):
            try:
                with st.spinner("Listening..."):
                    transcript = client.audio.transcriptions.create(
                        file=(
                            "message.wav",
                            audio.getvalue()
                        ),
                        model="whisper-large-v3-turbo"
                    )
                st.session_state.pending_prompt = transcript.text
                st.rerun()
            except Exception:
                st.error("Voice transcription failed.")

# ---------- TEXT INPUT ----------
typed_prompt = st.chat_input("Message Queen...")

prompt = st.session_state.pop(
    "pending_prompt", None
) or typed_prompt

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    try:
        with st.spinner("Queen is thinking..."):
            recent = st.session_state.messages[-20:]

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM},
                    *recent
                ],
                max_tokens=700
            )

            answer = response.choices[0].message.content

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        with st.chat_message("assistant"):
            st.write(answer)

    except Exception:
        st.error("Queen couldn't respond. Check your AI configuration.")

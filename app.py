import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title='QUEEN AI', page_icon='👑', layout='centered')
st.markdown('''<style>.block-container{max-width:720px;padding-top:2rem} h1{letter-spacing:.06em} .stChatMessage{border-radius:18px}</style>''', unsafe_allow_html=True)
st.title('👑 QUEEN AI')
st.caption('PROJECT QUEEN • Private beta • iPhone edition')
st.info('Prototype: chats stay in this browser session only. No permanent memory yet. Messages sent to the AI provider for processing.')

try:
    key = key = st.secrets['GROQ_API_KEY']
except (KeyError, FileNotFoundError):
    key = os.environ.get('GROQ_API_KEY')
if not key:
    st.error('The owner must configure OPENAI_API_KEY in the hosting service secrets before QUEEN can respond.')
    st.stop()

SYSTEM = '''You are QUEEN, a thoughtful, capable personal AI assistant for the owner of BARNONE, TMI (Tantalize My Intellect), and Circon Entertainment. Be articulate, warm, professional, direct, and resourceful. Help with creative writing, business planning, learning AI, and practical workflows. Do not claim human consciousness, physical presence, persistent memory, or actions you did not take. Ask permission before any consequential external action. Be clear about uncertainty. Never request or reveal passwords or API keys.'''
if 'messages' not in st.session_state:
    st.session_state.messages = []
with st.sidebar:
    st.header('QUEEN Controls')
    st.write('Model: gpt-4.1-mini')
    if st.button('Start new conversation'):
        st.session_state.messages = []
        st.rerun()
    st.download_button('Export this chat', data='\n\n'.join(f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages), file_name='queen_chat.txt', mime='text/plain')
    st.caption('Access control: keep your app private or add authentication before sharing its URL. API requests can incur charges.')
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])
if prompt := st.chat_input('Talk to QUEEN…'):
    st.session_state.messages.append({'role':'user','content':prompt})
    with st.chat_message('user'):
        st.markdown(prompt)
    with st.chat_message('assistant'):
        try:
            client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1", timeout=30.0)
            recent = st.session_state.messages[-20:]
                        response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM}, *recent],
                max_tokens=700
            )
            answer = response.choices[0].message.content or 'No response received.'
            st.markdown(answer)
            st.session_state.messages.append({'role':'assistant','content':answer})
        except Exception:
            st.error('QUEEN could not connect. Check the cloud API key, billing, and service availability. Do not paste your key into chat.')

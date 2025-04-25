from openai import OpenAI
import json
import streamlit as st
from streamlit.components.v1 import html
import time
import base64
import subprocess
import os
import tempfile
import sys

tts_file = "tts_gtts.py"

def model_completion_to_list(completion):
    out = []
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            out.append(str(chunk.choices[0].delta.content))
    
    return out
        
def response(list, delay=0.05):
    for chunk in list:
        yield chunk
        time.sleep(delay)

st.set_page_config(
    page_title="McWhiz",
    page_icon="wizard-hat.png"
)
st.title("Legendary Chat With The Whiz")

if "messages" not in st.session_state:
    st.session_state.client = OpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = st.secrets["API_KEY"]
    )

    with open("memory.json", 'r') as f:
        conversation = json.load(f)["messages"]

    with open("qualities.json", 'r') as f:
        qualities = json.load(f)["messages"]
    
    conversation.append(0)
    if conversation[0] != {"role": "assistant", "content": "Address McWhiz by his name for a response!"}:
        conversation.insert(0, {"role": "assistant", "content": "Address McWhiz by his name for a response!"})
    conversation.pop(len(conversation) - 1)
    conversation.append({"role":"system","content": "User joins the chat..."})

    st.session_state.messages = conversation
    st.session_state.qualities = qualities

for message in st.session_state.messages:
    if message["role"] == "user" or message["role"] == "assistant":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Message McWhiz"):
    st.session_state.messages.append({"role":"user","content":prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    completion = st.session_state.client.chat.completions.create(
        model="nvidia/llama-3.1-nemotron-70b-instruct",
        messages=(st.session_state.qualities+st.session_state.messages),
        temperature=0.6,
        top_p=0.85,
        max_tokens=1024,
        stream=True
    )

    response_text = model_completion_to_list(completion)

    string_text = ''.join(response_text)


    with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.mp3') as tmp_file:
        tmp_name = tmp_file.name
        tmp_file.close()

    args = [string_text, tmp_name]

    try:
        print(f"Starting subprocess with args: {args}")
            
        process = subprocess.run(
            [f"{sys.executable}", tts_file, *args],
            capture_output=True,
            text=True
        )

        with open(tmp_name, "rb") as f:
            audio_bytes = f.read()
        
        b64 = base64.b64encode(audio_bytes).decode()

        audio_html = f"""
        <audio id="tts" controls autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        <script>
            const audio = document.getElementById("tts");
            audio.playbackRate = 2;  // Adjust playback speed
        </script>
        """

        html(audio_html)
        
        if process.returncode == 0:
            print("Script executed successfully:")
            print(process.stdout)
        else:
            print("Script failed with error:")
            print(process.stderr)
    except Exception as e:
        print(f"Error processing task {args}: {e}")
    finally:
        os.remove(tmp_name)

    with st.chat_message("assistant"):
        st.write_stream(response(response_text, delay=0.05))

    st.session_state.messages.append({"role":"assistant","content":string_text})


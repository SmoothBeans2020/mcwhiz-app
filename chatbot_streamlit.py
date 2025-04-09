from openai import OpenAI
import json
import streamlit as st
import time
import keyboard
import os
import psutil
import subprocess
import subprocess
import queue
import threading

tts_file = "tts_offline.py"

def process_queue(task_queue):
    while True:
        try:
            args = task_queue.get()
            if args is None:
                break
            print(f"Starting subprocess with args: {args}")
            
            process = subprocess.Popen(
                ["python", tts_file, *args],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            print(f"Subprocess {args} finished with return code {process.returncode}")
            print(f"Output: {stdout}")
            if stderr:
                print(f"Error: {stderr}")
        except Exception as e:
            print(f"Error processing task {args}: {e}")

def add_task(task_queue, args):
    task_queue.put(args)

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

st.title("Legendary Chat With The Whiz")

if "messages" not in st.session_state:
    st.session_state.client = OpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = "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"
    )

    with open("memory.json", 'r') as f:
        conversation = json.load(f)["messages"]

    with open("qualities.json", 'r') as f:
        qualities = json.load(f)["messages"]
    
    conversation.append(0)
    if conversation[0] != {"role": "assistant", "content": "Type 'Exit' to leave"}:
        conversation.insert(0, {"role": "assistant", "content": "Type 'Exit' to leave"})
    conversation.pop(len(conversation) - 1)
    conversation.append({"role":"system","content": "User joins the chat..."})

    st.session_state.messages = conversation
    st.session_state.qualities = qualities

task_queue = queue.Queue()

thread = threading.Thread(target=process_queue, args=(task_queue,), daemon=True)
thread.start()

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

    arg = string_text
    add_task(task_queue, [arg])

    with st.chat_message("assistant"):
        st.write_stream(response(response_text, delay=0.05))

    st.session_state.messages.append({"role":"assistant","content":string_text})


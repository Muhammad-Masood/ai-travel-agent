import openai
from openai import OpenAI
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
import streamlit as st
import pandas as pd
import numpy as np

def createClient(api_key: str) -> OpenAI:
    try:
        client: OpenAI = OpenAI(api_key=api_key)
        print(client)
        return client
    except:
        st.toast("Invalid API Key", icon="🚨")

def createAssistant(client: OpenAI) -> tuple[Assistant,Thread]:
    try:
        assistant: Assistant = client.beta.assistants.create(
        name="Tripper",
        instructions="You are a helpful travel agent assistant that will help global travelers find the best destinations. When any user ask you regarding any travel related query or ask for any advice regarding destinations, provide it with the best recommendations and information available.",
        model="gpt-3.5-turbo",
        tools=[
            {"type": "code_interpreter"},
            {"type": "retrieval"},
            {"type": "function"},
        ],
    )
        print(assistant)
        thread:Thread = client.beta.threads.create()
        return assistant,thread
    except:
        st.toast("Error creating Tripper or Invalid API Key", icon="🚨")

def createMessageAndRun(client:OpenAI, _thread_id:str, _content: str, _assistant_id:str):
    client.beta.threads.messages.create(
    thread_id=_thread_id,
    role="user",
    content=_content
    )
    run = client.beta.threads.runs.create(
    thread_id=_thread_id,
    assistant_id=_assistant_id,
    )


with st.sidebar:
    st.title("Create Tripper")
    openai_api_key: str = st.text_input(
        "Enter your OpenAI api key to create an assistant", type="password"
    )
    if openai_api_key:
        client: OpenAI = createClient(openai_api_key)
        createAssistant(client=client)
    st.title("Already Created Tripper?")
    st.text("Or access your assistant directly if already created")
    api_key: str = st.text_input(
        "OpenAI API key", key="openai_api_key", type="password"
    )
    if(api_key):
        client: OpenAI = createClient(api_key)
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[![View the source code](https://github.com/codespaces/badge.svg)]()"

st.title("🗺️ Tripper")
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I assist you?"}
    ]
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    # msg = # get response from assistant
    # st.session_state.append(msg)
    # st.chat_message("assistant").write(msg.content)

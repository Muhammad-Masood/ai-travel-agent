import streamlit as st
import pandas as pd
import numpy as np
import time
from model import ClientModel, AssistantModel
from openai.types.beta.threads.thread_message import ThreadMessage

assistantModel: AssistantModel = AssistantModel()
clientModel: ClientModel = ClientModel()
if "assistant_model" not in st.session_state:
    st.session_state["assistant_model"] = assistantModel
if "client_model" not in st.session_state:
    st.session_state["client_model"] = clientModel

with st.sidebar:
    st.title("Create Tripper")
    openai_api_key1: str = st.text_input(
        "Enter your OpenAI api key to create an assistant",
        type="password",
        key="openai_api_key1",
    )
    if openai_api_key1 and "assistant_created" not in st.session_state:
        try:
            st.session_state.client_model.createClient(openai_api_key1)
            st.session_state.assistant_model.createAssistant(clientModel.retrieveClient())
            st.write("Your Tripper ID",st.session_state.assistant_model.getAssistant().id)
            st.session_state["assistant_created"] = True
            st.toast("Tripper Created Successfully.", icon="✅")
        except Exception as e:
            st.toast(f"error: {e}", icon="🚨")
    st.title("Already Created Tripper?")
    st.text("Or access your assistant directly if already created")
    openai_api_key2: str = st.text_input(
        "OpenAI API key", key="openai_api_key2", type="password"
    )
    assistant_id: str = st.text_input("Tripper ID", key="assistant_id")
    if openai_api_key2 and assistant_id and "assistant_recovered" not in st.session_state:
        try:
            print("recovering tripper...")
            st.session_state.client_model.createClient(openai_api_key2)
            st.session_state.assistant_model.setAssistantById(assistant_id, st.session_state.client_model.retrieveClient())
            st.session_state.assistant_model.createThread(st.session_state.client_model.retrieveClient())
            st.session_state["assistant_recovered"] = True
            st.toast("Tripper Recovered Successfully.", icon="✅")
        except Exception as e:
            st.toast(f"error: {e}", icon="🚨")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

st.title("🗺️ Tripper")
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I assist you?"}
    ]
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key1 and not openai_api_key2:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    messages = st.session_state.assistant_model.createAndRunMessage(prompt, st.session_state.client_model.retrieveClient())
    print(messages)
    st.session_state.messages.append({"role": "assistant", "content": messages.data[0].content[0].text.value})
    st.chat_message("assistant").write(messages.data[0].content[0].text.value)

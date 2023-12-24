import streamlit as st
import pandas as pd
import os
import numpy as np
import time
from model import ClientModel, AssistantModel
from openai.types.beta.threads.thread_message import ThreadMessage
import plotly.graph_objects as go
from dotenv import load_dotenv, find_dotenv
from streamlit_geolocation import streamlit_geolocation
import geocoder

assistantModel: AssistantModel = AssistantModel()
clientModel: ClientModel = ClientModel()

if "assistant_model" not in st.session_state:
    st.session_state["assistant_model"] = assistantModel
if "client_model" not in st.session_state:
    st.session_state["client_model"] = clientModel

# with open("style.css") as style:
#     st.markdown(f'<style>{style.read()}</style>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

# if(st.session_state["marked_latitudes"] is None and st.session_state["marked_latitudes"] is None):
# Get user's current location
g = geocoder.ip("me")
st.session_state["marked_latitudes"] = [g.latlng[0]]
st.session_state["marked_longitudes"] = [g.latlng[1]]


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
            st.session_state.assistant_model.createAssistant(
                clientModel.retrieveClient()
            )
            st.write(
                "Your Tripper ID", st.session_state.assistant_model.getAssistant().id
            )
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
    if (
        openai_api_key2
        and assistant_id
        and "assistant_recovered" not in st.session_state
    ):
        try:
            print("recovering tripper...")
            st.session_state.client_model.createClient(openai_api_key2)
            st.session_state.assistant_model.setAssistantById(
                assistant_id, st.session_state.client_model.retrieveClient()
            )
            st.session_state.assistant_model.createThread(
                st.session_state.client_model.retrieveClient()
            )
            st.session_state["assistant_recovered"] = True
            st.toast("Tripper Recovered Successfully.", icon="✅")
        except Exception as e:
            st.toast(f"error: {e}", icon="🚨")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

with col1:
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
    messages = st.session_state.assistant_model.createAndRunMessage(
        prompt, st.session_state.client_model.retrieveClient()
    )
    print(messages)
    st.session_state.messages.append(
        {"role": "assistant", "content": messages.data[0].content[0].text.value}
    )
    st.chat_message("assistant").write(messages.data[0].content[0].text.value)

with col2:
    _: bool = load_dotenv(find_dotenv())
    fig = go.Figure(
        go.Scattermapbox(
            mode="markers",
            lon=st.session_state["marked_longitudes"],
            lat=st.session_state["marked_latitudes"],
            marker=go.scattermapbox.Marker(
                size=15,
                symbol="marker"
            ),
            text=[g.city],
        )
    )
    fig.update_layout(
        margin={"l": 0, "t": 0, "b": 0, "r": 0},
        mapbox={
            "accesstoken": os.getenv("MAPBOX_ACCESS_TOKEN"),
            "zoom": 0.5,
            # "center":go.layout.mapbox.Center(
            #     lat=st.session_state["user_lat"],
            #     lon=st.session_state["user_lon"]
            # )
        },
        height=400,
    )
    st.plotly_chart(fig, config={"displayModeBar": False}, use_container_width=True)

    st.button("Update map")
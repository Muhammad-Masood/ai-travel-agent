import time
import openai
from openai import OpenAI
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.threads.run import Run
from openai.types.beta.threads.thread_message import ThreadMessage


class ClientModel:
    def createClient(self, _api_key: str) -> OpenAI:
        self.client = OpenAI(api_key=_api_key)

    def retrieveClient(self) -> OpenAI:
        return self.client


class AssistantModel:
    def __init__(self) -> None:
        pass

    def createAssistant(self, client: OpenAI) -> Assistant:
        self.assistant: Assistant = client.beta.assistants.create(
            name="Tripper",
            instructions="You are a helpful travel agent assistant that will help global travelers find the best destinations. When any user ask you regarding any travel related query or ask for any advice regarding destinations, provide it with the best recommendations and information available.",
            model="gpt-3.5-turbo",
            tools=[{"type": "code_interpreter"}],
        )
        return self.assistant

    def setAssistantById(self, _id: str, _client: OpenAI) -> None:
        self.assistant = _client.beta.assistants.retrieve(assistant_id=_id)

    def getAssistant(self) -> Assistant:
        return self.assistant

    def createThread(self, _client: OpenAI) -> None:
        self.thread = _client.beta.threads.create()

    def createAndRunMessage(self, _content: str, _client: OpenAI):
        _client.beta.threads.messages.create(
            self.thread.id, role="user", content=_content
        )
        self.run: Run = _client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )
        while self.run.status == "queued" or self.run.status == "in_progress":
            self.run = _client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=self.run.id)
            time.sleep(0.5)
        self.messages = _client.beta.threads.messages.list(thread_id=self.thread.id)
        return self.messages


from pydantic import BaseModel, Field

from promptulate import chat
from promptulate.llms import BaseLLM
from promptulate.schema import AssistantMessage, BaseMessage, MessageSet, UserMessage


class FakeLLM(BaseLLM):
    llm_type: str = "fake"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, prompt: str, *args, **kwargs):
        return "fake response"

    def _predict(self, prompts: MessageSet, *args, **kwargs) -> BaseMessage:
        content = "fake response"

        if "Output format" in prompts.messages[-1].content:
            content = """{"city": "Shanghai", "temperature": 25}"""

        return AssistantMessage(content=content)


class Response(BaseModel):
    city: str = Field(description="city name")
    temperature: float = Field(description="temperature")


def test_general_chat():
    llm = FakeLLM()

    # test general chat
    answer = chat("hello", model="fake", custom_llm=llm)
    assert answer == "fake response"

    # test messages is MessageSet
    messages = MessageSet(
        messages=[UserMessage(content="hello"), AssistantMessage(content="fake")]
    )
    answer = chat(messages, model="fake", custom_llm=llm)
    assert answer == "fake response"

    # test messages is list
    messages = [{"content": "Hello, how are you?", "role": "user"}]
    answer = chat(messages, model="fake", custom_llm=llm)
    assert answer == "fake response"


def test_chat_response():
    llm = FakeLLM()

    # test original response
    answer = chat("hello", model="fake", custom_llm=llm, is_message_return_type=True)
    assert isinstance(answer, BaseMessage)
    assert answer.content == "fake response"

    # test formatter response
    answer = chat(
        "what's weather tomorrow in shanghai?",
        model="fake",
        output_schema=Response,
        custom_llm=llm,
    )
    assert isinstance(answer, Response)
    assert getattr(answer, "city", None) == "Shanghai"
    assert getattr(answer, "temperature", None) == 25

    # test formatter response with examples
    examples = [
        Response(city="Shanghai", temperature=25),
        Response(city="Beijing", temperature=30),
    ]
    answer = chat(
        "what's weather tomorrow in shanghai?",
        model="fake",
        output_schema=Response,
        examples=examples,
        custom_llm=llm,
    )
    assert isinstance(answer, Response)
    assert getattr(answer, "city", None) == "Shanghai"
    assert getattr(answer, "temperature", None) == 25


# def test_chat_with_gpt():
#     # test gpt-3.5
#     answer = chat("hello")
#     assert isinstance(answer, str)
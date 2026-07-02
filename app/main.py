from fastapi import FastAPI
from pydantic import BaseModel

from app.guardrails import (
    is_off_topic,
    is_prompt_injection,
    refusal_reply,
)
from app.recommender import latest_user_text, recommend


app = FastAPI(title="SHL Assessment Recommender")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str


class ChatResponse(BaseModel):
    reply: str
    recommendations: list[Recommendation]
    end_of_conversation: bool


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    messages = [message.model_dump() for message in request.messages]
    latest_text = latest_user_text(messages)
    print("LATEST:", repr(latest_text))
    print("OFF_TOPIC:", is_off_topic(latest_text))
    
    if is_prompt_injection(latest_text) or is_off_topic(latest_text):
        return ChatResponse(
            reply=refusal_reply(),
            recommendations=[],
            end_of_conversation=False,
        )

    reply, recommendations, end_of_conversation = recommend(messages)

    return ChatResponse(
        reply=reply,
        recommendations=recommendations,
        end_of_conversation=end_of_conversation,
    )
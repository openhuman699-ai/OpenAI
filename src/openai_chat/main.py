from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel, Field

load_dotenv()

DEFAULT_MODEL = "gpt-4.1-mini"
STATIC_DIR = Path(__file__).parent / "static"


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=20_000)


class ChatRequest(BaseModel):
    messages: list[Message] = Field(min_length=1, max_length=50)


class ChatResponse(BaseModel):
    message: Message
    model: str


def get_model() -> str:
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL)


def is_configured() -> bool:
    return bool(os.getenv("CHAT_API_KEY"))


async def generate_reply(messages: list[Message]) -> ChatResponse:
    if not is_configured():
        raise HTTPException(
            status_code=503,
            detail="CHAT_API_KEY is not configured for this environment.",
        )

    model = get_model()
    client = AsyncOpenAI(api_key=os.environ["CHAT_API_KEY"])
    try:
        result = await client.chat.completions.create(
            model=model,
            messages=[message.model_dump() for message in messages],
        )
    except OpenAIError as error:
        raise HTTPException(status_code=502, detail="The model provider request failed.") from error

    content = result.choices[0].message.content
    if not content:
        raise HTTPException(status_code=502, detail="The model returned an empty response.")
    return ChatResponse(message=Message(role="assistant", content=content), model=model)


app = FastAPI(
    title="OpenAI Chat",
    description="A minimal web chat backed by the OpenAI API.",
    version="0.1.0",
)


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, str | bool]:
    return {"status": "ok", "openai_configured": is_configured(), "model": get_model()}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await generate_reply(request.messages)

"""
FastAPI RAG Server - OpenAI-Compatible API for Open WebUI

This server provides OpenAI-compatible endpoints that:
1. GET /v1/models - Returns available models for Open WebUI discovery
2. POST /v1/chat/completions - RAG-enhanced chat with streaming support

The server bridges Open WebUI → RAG Pipeline → Ollama with true streaming.
"""

import json
import time
import uuid
from typing import List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .database import VectorDatabase
from .ollama_client import OllamaClient


# Initialize FastAPI app
app = FastAPI(
    title="RAG API Server",
    description="OpenAI-compatible RAG API for Open WebUI",
    version="1.0.0"
)

# Add CORS middleware for Open WebUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = VectorDatabase()
ollama = OllamaClient()


# Pydantic models for request/response
class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: Optional[bool] = True
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None


# System prompt for RAG
SYSTEM_PROMPT = """אתה עוזר חכם שמטרתו לענות על שאלות בהתבסס על מידע מוסמך.
הוראות:
1. ענה בעברית בלבד
2. השתמש רק במידע שסופק בקונטקסט
3. אם המידע בקונטקסט לא מספיק, ציין זאת
4. שמור על תשובה ברורה וממוקדת
5. אם יש מספר נקודות חשובות, פרט אותן בנקודות"""


@app.get("/v1/models")
async def list_models():
    """Return available models for Open WebUI discovery."""
    return {
        "object": "list",
        "data": [
            {
                "id": "rag-model",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "local",
                "permission": [],
                "root": "rag-model",
                "parent": None
            }
        ]
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    Handle chat completions with RAG enhancement.
    
    Flow:
    1. Extract last user message
    2. Query vector database for relevant context (parent documents)
    3. Build prompt with context
    4. Stream response from Ollama in OpenAI format
    """
    # Extract the last user message
    user_message = ""
    for msg in reversed(request.messages):
        if msg.role == "user":
            user_message = msg.content
            break
    
    if not user_message:
        return JSONResponse(
            status_code=400,
            content={"error": "No user message found"}
        )
    
    # Query vector database with parent context
    print(f"\n[RAG] Query: {user_message[:100]}...")
    results = db.query_with_parent_context(user_message, k=3, score_threshold=0.1)
    
    # Build context from parent documents (broader context)
    context_parts = []
    for i, result in enumerate(results, 1):
        # Prefer parent content for broader context, fall back to child
        content = result.get('parent_content') or result.get('child_content', '')
        score = result.get('similarity_score', 0)
        if content:
            context_parts.append(f"[מקור {i}] (דמיון: {score:.2%})\n{content}")
    
    context = "\n\n".join(context_parts) if context_parts else "לא נמצא מידע רלוונטי במאגר."
    print(f"[RAG] Found {len(results)} relevant documents")
    
    # Build the prompt with context
    prompt = f"""מידע רלוונטי מהמאגר:
{context}

שאלת המשתמש: {user_message}

בהתבסס על המידע שסופק, ענה על השאלה:"""

    if request.stream:
        # Streaming response
        async def generate():
            async for chunk in ollama.stream_chat(prompt, SYSTEM_PROMPT):
                yield chunk
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    else:
        # Non-streaming response
        response_text = await ollama.chat(prompt, SYSTEM_PROMPT)
        
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "rag-model",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "chunks_in_db": db.get_total_chunks()}

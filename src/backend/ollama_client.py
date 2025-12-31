"""
Async Ollama Client for Streaming LLM Responses

This module provides an async client for Ollama that:
- Streams responses in real-time using httpx.AsyncClient
- Converts Ollama format to OpenAI delta format on-the-fly
- Supports air-gapped operation with local Ollama server
"""

import json
import uuid
import time
from typing import AsyncGenerator, Optional

import httpx

from ..utils.config import load_config


class OllamaClient:
    """Async client for Ollama API with streaming support."""
    
    def __init__(self):
        config = load_config()
        self.base_url = config.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = config.get("OLLAMA_MODEL", "llama3.2")
    
    async def stream_chat(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion from Ollama and yield OpenAI-formatted SSE chunks.
        
        Args:
            prompt: The user's prompt with context
            system_prompt: Optional system prompt
            
        Yields:
            Server-Sent Event formatted strings in OpenAI delta format
        """
        chat_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        created = int(time.time())
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise Exception(f"Ollama error {response.status_code}: {error_text}")
                
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    try:
                        ollama_chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    
                    # Extract content from Ollama response
                    content = ollama_chunk.get("message", {}).get("content", "")
                    done = ollama_chunk.get("done", False)
                    
                    if content:
                        # Convert to OpenAI delta format
                        openai_chunk = {
                            "id": chat_id,
                            "object": "chat.completion.chunk",
                            "created": created,
                            "model": "rag-model",
                            "choices": [{
                                "index": 0,
                                "delta": {"content": content},
                                "finish_reason": None
                            }]
                        }
                        yield f"data: {json.dumps(openai_chunk)}\n\n"
                    
                    if done:
                        # Send final chunk with finish_reason
                        final_chunk = {
                            "id": chat_id,
                            "object": "chat.completion.chunk",
                            "created": created,
                            "model": "rag-model",
                            "choices": [{
                                "index": 0,
                                "delta": {},
                                "finish_reason": "stop"
                            }]
                        }
                        yield f"data: {json.dumps(final_chunk)}\n\n"
                        yield "data: [DONE]\n\n"
                        break
    
    async def chat(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Non-streaming chat completion from Ollama.
        
        Args:
            prompt: The user's prompt with context
            system_prompt: Optional system prompt
            
        Returns:
            Complete response text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama error {response.status_code}: {response.text}")
            
            data = response.json()
            return data.get("message", {}).get("content", "")


# Create a singleton instance
ollama_client = OllamaClient()

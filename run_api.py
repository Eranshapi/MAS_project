"""
Run the FastAPI RAG Server

Usage:
    python run_api.py

The server will start at http://0.0.0.0:8000
Configure Open WebUI with Base URL: http://<your-ip>:8000/v1
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("FastAPI RAG Server for Open WebUI")
    print("=" * 60)
    print("\nEndpoints:")
    print("  - GET  /v1/models           - List available models")
    print("  - POST /v1/chat/completions - Chat with RAG")
    print("  - GET  /health              - Health check")
    print("\nOpen WebUI Base URL: http://<your-ip>:8000/v1")
    print("=" * 60)
    
    uvicorn.run(
        "src.backend.api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )

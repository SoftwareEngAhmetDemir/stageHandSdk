from typing import List
from ollama import Client
from schemas import Message
import asyncio

async def ask_ollama(model_name: str, messages: List[dict]) -> str:
    client = Client()
    
    # Wrap sync client.chat in a thread
    response = await asyncio.to_thread(lambda: client.chat(model=model_name, messages=messages))
    
    # Ollama response object has .message['content']
    return response['message']['content']

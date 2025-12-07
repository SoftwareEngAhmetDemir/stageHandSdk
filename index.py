import asyncio
from llm.ask_ollama import ask_ollama
from llm.prompt import SYSTEM_PROMPT_TEXT, ASSISTANT_TEXT
from typing import List
from schemas import Message

async def main():
    modelText = "qwen2.5-coder:14b"  # replace with your model

    conversation = [
    {"role": "system", "content": SYSTEM_PROMPT_TEXT},
    {"role": "assistant", "content": ASSISTANT_TEXT},
    {"role": "user", "content": "Go to https://www.facebook.com/reg/ , fill firstname with ahmet and last name with demir."},
    ]

    reply = await ask_ollama(modelText, conversation)
    print(reply)

    
if __name__ == "__main__":
    asyncio.run(main())
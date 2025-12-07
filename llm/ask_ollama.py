from typing import List
from ollama import Client
from ..schemas import Message  # ✅ Fixed

async def ask_ollama(model_name: str, messages: List[Message]) -> str:
    
    client = Client()
    
    response = await client.chat(model=model_name, messages=messages)
    return response['message']['content']



# Example usage:
# import asyncio
# from ..schemas import Message

# async def main():
    # conversation = [
    #     Message(role="user", content="Hello!"),
    #     Message(role="assistant", content="Hi there!"),
    #     Message(role="user", content="How are you?")
    # ]

    # reply = await ask_ollama("llama2", conversation)
    # print(reply)

# if __name__ == "__main__":
#    asyncio.run(main())
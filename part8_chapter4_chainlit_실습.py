import chainlit as cl

import requests
import json

# Ollama API 주소와 모델 설정
API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3B"


# Function to interact with the Ollama API and get a streaming response
async def fetch_response_stream(question):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    payload = {
        "model": MODEL_NAME,
        "prompt": question,
        "stream": True  # Enable streaming if supported by the API
    }

    try:
        # Start the streaming request
        with requests.post(API_URL, headers=headers, data=json.dumps(payload), stream=True) as response:
            response.raise_for_status()  # Raise error for bad responses
            # Yield each line (or chunk) as it’s received
            for chunk in response.iter_lines():
                if chunk:
                    # Decode and parse the JSON response
                    data = json.loads(chunk.decode('utf-8'))
                    # Extract the response text
                    yield data.get("response", "")
    except requests.exceptions.RequestException as e:
        yield f"Error: {e}"


# Event handler for receiving user messages
@cl.on_message
async def on_message(message: cl.Message):
    # Retrieve conversation history from the session, or initialize it
    conversation_history = cl.user_session.get("conversation_history", [])
    conversation_history.append({"role": "user", "content": message.content})

    # Prepare the prompt with conversation history for context
    prompt = "\n".join([f"{entry['role']}: {entry['content']}" for entry in conversation_history])
    
    # Initialize Chainlit message for streaming response
    msg = cl.Message(content="")

    # Stream the response from the Ollama API
    async for chunk in fetch_response_stream(prompt):
        await msg.stream_token(chunk)  # Stream each chunk to the user in real-time

    # Finalize and send the complete message
    await msg.send()

    # Add the assistant's response to the conversation history
    conversation_history.append({"role": "assistant", "content": msg.content})
    cl.user_session.set("conversation_history", conversation_history)


# Event that triggers when a new chat session starts
@cl.on_chat_start
async def on_chat_start():
    # Set a welcome message and initialize the session
    welcome_message = "You're now connected with the llama3.2:3B model. Ask away!"
    await cl.Message(content=welcome_message).send()
    cl.user_session.set("conversation_history", [])
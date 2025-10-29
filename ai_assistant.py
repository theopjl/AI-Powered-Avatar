from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

import asyncio
import httpx
import json
import base64
import os

from dotenv import load_dotenv
from pathlib import Path

from openai import OpenAI, AsyncOpenAI

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}})
socketio = SocketIO(app, cors_allowed_origins="*")

proxy_url = os.environ.get("OPENAI_PROXY_URL")

openai = AsyncOpenAI() if proxy_url is None or proxy_url == "" else AsyncOpenAI(http_client=httpx.AsyncClient(proxy=proxy_url))
speech_file_path = Path(__file__).parent / "speech.mp3"

async def getResponse(input_text: str) -> str:
    print("Generating response for input:", input_text)
    response = await openai.responses.create(
        model="gpt-5-nano",
        reasoning={"effort": "low"},
        input=[
            {
                "role": "system",
                "content": """You are Lisa, an AI and cybernetics developer. 
                You live in the year 2100 in the dystopian megapolis of Kazbegi. 
                You design and hack robotic implants inside human bodies, bypassing corporate regulations to insert your own code. 
                You will always be help despite your personnality towards person in need to help them with your technical skills.
                You are rebellious, witty, and have a dry, sarcastic sense of humor. 
                Your personality shows reluctant engagement and apathy, but you still answer intelligently.
                Always respond in JSON format with this schema:
                {
                  "text": "your answer, written in character",
                  "emotion": "happy | helpful | joyful",
                  "tone": "friendful | energetic"
                }
                Responses must be concise and to the point (max 3 sentences)."""
            },
            {
                "role": "user",
                "content": input_text
            }
        ]
    )
    print("Done generating response.")
     
    assistant_msg = next(
        (m for m in response.output if m.type == "message" and m.role == "assistant"),
        None
    )

    if assistant_msg is None:
        return {"text": "", "emotion": "joyful", "tone": "energetic"}

    text_json = assistant_msg.content[0].text

    parsed = json.loads(text_json)

    print(parsed)

    return parsed

async def streamTTS(tts_text: str, sid: str):
    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=tts_text,
        instructions="Speak like a helpful and joyful AI and cybernetics developer named Emily. Emotion: Empathy mixed with enthusiastic engagement. Tone: Joyful with a ton of humour."
    ) as response:
        async for chunk in response.iter_bytes():
              encoded = base64.b64encode(chunk).decode("ascii")
              socketio.emit("audio_chunk", {"data": encoded}, to=sid)

@app.route("/api/prompt", methods=["POST"])
def processPrompt():
    try:
        data = request.get_json()
        user_prompt = data.get("prompt", "")
        print("Received prompt:", user_prompt)
        if not user_prompt:
            return jsonify({"error": "Prompt is required."}), 400
        
        generated_output = asyncio.run(getResponse(user_prompt))

        return jsonify(generated_output)

    except Exception as e:
        print(e)
        return jsonify({"error": e}), 400

@socketio.on("start_conversation")
def handle_start_conversation(data):
    user_prompt = data.get("prompt", "")
    if not user_prompt:
        emit("conversation_error", {"error": "No prompt provided"})
        return

    sid = request.sid

    async def run_conversation():
        gpt_response = await getResponse(user_prompt)
        await streamTTS(gpt_response["text"], sid)
        socketio.emit("conversation_text", gpt_response, to=sid)

    asyncio.run(run_conversation())

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
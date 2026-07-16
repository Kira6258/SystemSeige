import os
from groq import Groq

# Load environment variable for Groq API Key
from dotenv import load_dotenv
load_dotenv()

client = Groq()
try:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Output JSON with key 'response'."},
            {"role": "user", "content": "Hello"}
        ],
        response_format={"type": "json_object"}
    )
    print("Success:", response.choices[0].message.content)
except Exception as e:
    print("Groq Error:", str(e))

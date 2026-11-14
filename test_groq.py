
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import os

# Load the exact project .env file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path, override=True)

api_key = os.getenv("GROQ_API_KEY", "").strip()

print("ENV FILE FOUND:", env_path.exists())
print("API KEY PRESENT:", bool(api_key))
print("API KEY LENGTH:", len(api_key))
print("API KEY PREFIX VALID:", api_key.startswith("gsk_"))

try:
    client = Groq(api_key=api_key)

    result = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "user", "content": "Reply with NOVA ONLINE"}
        ],
        max_completion_tokens=50
    )

    print("\nGROQ AUTHENTICATION: SUCCESS")
    print("RESPONSE:", result.choices[0].message.content)

except Exception as error:
    print("\nGROQ AUTHENTICATION: FAILED")
    print(type(error).__name__)
    print(str(error))

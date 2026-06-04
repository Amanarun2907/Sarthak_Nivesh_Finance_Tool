from dotenv import load_dotenv
import os, requests, sys
load_dotenv()
key = os.getenv("GROQ_API_KEY", "")
print("Key length:", len(key))
print("Key prefix:", key[:8] if len(key) > 8 else "TOO SHORT")
r = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json={"model": "llama-3.3-70b-versatile",
          "messages": [{"role": "user", "content": "Say: GROQ_WORKS"}],
          "max_tokens": 10},
    timeout=20,
)
print("Status:", r.status_code)
if r.status_code == 200:
    print("Response:", r.json()["choices"][0]["message"]["content"])
else:
    print("Error:", r.text[:300])
    sys.exit(1)

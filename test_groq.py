from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

response = client.chat.completions.create(
    model="llama-3.1-70b-versatile",
    messages=[{"role": "user", "content": "Say 'Hello, I work!' in exactly 3 words"}],
    temperature=0
)

print(response.choices[0].message.content)

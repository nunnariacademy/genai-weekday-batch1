from mem0 import MemoryClient
from dotenv import load_dotenv
import os

load_dotenv()

mem0_api_key = os.getenv("MEM0_API_KEY")
client = MemoryClient(api_key=mem0_api_key)

messages = [
    {"role": "user", "content": "Hi, I'm Shiva and I'm a vegetarian and allergic to nuts."},
    {"role": "assistant", "content": "Got it! I'll remember your dietary preferences."}
]

client.add(messages, user_id = "user_1")


results = client.search("What are the foods Shiva is allergic to?", filters={"user_id": "user_1"})
print(results)


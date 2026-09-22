import os
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
url = "https://api.groq.com/openai/v1/models"
headers = {"Authorization": f"Bearer {api_key}"}

response = requests.get(url, headers=headers)
for model in response.json().get("data", []):
    print(model["id"])
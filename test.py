import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv("api.env")

genai.configure(api_key=os.getenv("API_KEY"))

model = genai.GenerativeModel("models/gemini-flash-lite-latest")

response = model.generate_content("Hello")

print(response.text)
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models_to_test = [
    "models/gemini-1.5-flash",
    "models/gemini-2.0-flash-lite-preview-02-05",
    "models/gemini-2.0-flash"
]

for model_name in models_to_test:
    print(f"Testing {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hi")
        print(f"Success with {model_name}")
        break
    except Exception as e:
        print(f"Failed {model_name}: {e}")

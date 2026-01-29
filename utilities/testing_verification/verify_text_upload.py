import requests
import sys
import os

API_URL = "http://localhost:8000"
FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../vector_db/data.txt")

def upload_file():
    print(f"Uploading {FILE_PATH} to {API_URL}/documents/upload...")
    try:
        with open(FILE_PATH, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{API_URL}/documents/upload", files=files)
            
        if response.status_code == 200:
            print("✅ Upload Success!")
            print(response.json())
        else:
            print(f"❌ Upload Failed: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {API_URL}. Is the backend running?")

if __name__ == "__main__":
    upload_file()

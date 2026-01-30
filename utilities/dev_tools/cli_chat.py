import requests
import json
import sys
import time

# Configuration
API_URL = "http://localhost:8000/whatsapp/message"
DEFAULT_PHONE = "94770000000"

def chat_loop():
    print("="*50)
    print("🤖 Power Lanka CLI Chat Client")
    print("="*50)
    print(f"Connecting to: {API_URL}")
    print("Type 'quit' or 'exit' to stop.\n")
    
    phone_number = input(f"Enter Phone Number for session (default {DEFAULT_PHONE}): ").strip()
    if not phone_number:
        phone_number = DEFAULT_PHONE
        
    print(f"\n✅ Session initialized for: {phone_number}\n")
    
    while True:
        try:
            user_input = input("You > ").strip()
            if user_input.lower() in ['quit', 'exit']:
                break
            if not user_input:
                continue
                
            # Prepare Payload
            payload = {
                "phone_number": phone_number,
                "message": user_input
            }
            
            # Send Request
            try:
                # Show loading indicator
                sys.stdout.write("Bot is thinking...")
                sys.stdout.flush()
                
                response = requests.post(API_URL, json=payload)
                sys.stdout.write("\r" + " "*20 + "\r") # Clear loading text
                
                if response.status_code == 200:
                    data = response.json()
                    bot_reply = data.get("response", "No response text")
                    print(f"Bot > {bot_reply}\n")
                    
                    if data.get("category_image"):
                        print(f"[Details] Image suggested: {data.get('category_image')}\n")
                else:
                    print(f"\n[Error] Server returned {response.status_code}: {response.text}\n")
                    
            except requests.exceptions.ConnectionError:
                sys.stdout.write("\r" + " "*20 + "\r")
                print("\n[Error] Could not connect to backend at localhost:8000. Is the server running?\n")
            except Exception as e:
                sys.stdout.write("\r" + " "*20 + "\r")
                print(f"\n[Error] {e}\n")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    chat_loop()

from google import genai
import os

GEMINI_API_KEY = "AIzaSyDepyqmcOhdJUbxjAuOOyWvyfDpsrOLD0k"

def main():
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("--- Testing Model List ---")
        for m in client.models.list():
            print(f"Model ID: {m.name}")
            
        print("\n--- Testing Content Generation ---")
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Say Hello!"
        )
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"\n--- ERROR ---")
        print(e)

if __name__ == "__main__":
    main()

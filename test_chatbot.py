import requests
import json

url = "http://localhost:5000/api/chat"

test_messages = [
    "I'm feeling really sad because I failed my exam",
    "I have severe anxiety about my job interview",
    "I'm struggling with depression",
]

for message in test_messages:
    payload = {"message": message}
    response = requests.post(url, json=payload)
    result = response.json()
    
    print(f"User: {message}")
    print(f"Emotion: {result['emotion']}")
    print(f"Response: {result['response']}\n")
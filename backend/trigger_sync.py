import urllib.request
import json

try:
    req = urllib.request.Request("http://127.0.0.1:8000/api/ai/sync-class-notes", method="POST")
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print(f"Response: {response.read().decode()}")
except Exception as e:
    print(f"Error: {e}")

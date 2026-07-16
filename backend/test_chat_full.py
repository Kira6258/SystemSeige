import requests
import uuid

BASE_URL = "http://localhost:8000/api"

uid = str(uuid.uuid4())[:8]
email = f"test_{uid}@example.com"
password = "Password123"

print("Creating user:", email)
session = requests.Session()

# 1. Register a test user
res = session.post(f"{BASE_URL}/auth/register", json={
    "email": email,
    "password": password
})
print("Register status:", res.status_code)

# 2. Login to get token (sets cookies on session)
res = session.post(f"{BASE_URL}/auth/login", json={
    "email": email,
    "password": password
})
print("Login status:", res.status_code)

if res.status_code == 200:
    # 3. Hit chat (cookies are automatically sent)
    print("Hitting chat...")
    chat_res = session.post(f"{BASE_URL}/chat", json={
        "message": "how do I buy a car?"
    })
    print("Chat status:", chat_res.status_code)
    print("Chat body:", chat_res.text)
else:
    print("Login body:", res.text)

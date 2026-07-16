import urllib.request
import json
import urllib.error

url = 'http://localhost:8000/api/auth/login'
data = json.dumps({"email": "kishoremessi1007@gmail.com", "password": "test"}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')

try:
    with urllib.request.urlopen(req) as f:
        print("Status:", f.status)
        print("Response:", f.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Status:", e.code)
    print("Headers:", e.headers)
    print("Response:", e.read().decode('utf-8'))

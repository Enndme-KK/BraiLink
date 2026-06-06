"""Test chat API with proper auth."""
import httpx, json, os, sys

sys.path.insert(0, r'C:\Users\Kennys\Desktop\BraiLink\code\backend\ml_service')

# First verify module-level URL
from deepseek_client import DEEPSEEK_API_URL
print(f'Module DEEPSEEK_API_URL: {DEEPSEEK_API_URL}')
assert DEEPSEEK_API_URL.endswith('/chat/completions'), f'URL still wrong: {DEEPSEEK_API_URL}'

# Now test via HTTP with Django token
url = 'http://localhost:8000/api/ml/chat'
data = {
    'messages': [{'role': 'user', 'content': 'Hello'}],
    'patient_info': {}
}

# First try without auth
resp1 = httpx.post(url, headers={'Content-Type': 'application/json'}, json=data, timeout=10)
print(f'No auth: {resp1.status_code}')

# Get a token by logging in
login_url = 'http://localhost:8000/api/auth/login/'
login_data = {'username': 'patient1', 'password': 'patient123'}
try:
    resp = httpx.post(login_url, headers={'Content-Type': 'application/json'}, json=login_data, timeout=10)
    print(f'Login: {resp.status_code}')
    if resp.status_code == 200:
        token = resp.json().get('token', '')
        print(f'Token: {token[:20]}...')

        headers = {'Content-Type': 'application/json', 'Authorization': f'Token {token}'}
        resp2 = httpx.post(url, headers=headers, json=data, timeout=60)
        print(f'Chat status: {resp2.status_code}')
        print(f'Chat response: {resp2.text[:300]}')
    else:
        print(f'Login failed: {resp.text}')
except Exception as e:
    print(f'Error: {e}')

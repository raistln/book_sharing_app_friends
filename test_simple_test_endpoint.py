import requests

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0YjdlM2JiYi1lNTMxLTQwODYtYmNhYy05YzUxMjllOGM1MmMiLCJleHAiOjE3NjA5OTg2OTB9.kN_Kn6BYebk0WI78ny1VunqZ0-DzOM52QwHwzdmHKZA"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Test endpoint de prueba
print("Test: Endpoint de prueba /search/test")
response = requests.get(
    "http://localhost:8000/search/test",
    headers=headers
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

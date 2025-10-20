import requests

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0YjdlM2JiYi1lNTMxLTQwODYtYmNhYy05YzUxMjllOGM1MmMiLCJleHAiOjE3NjA5OTg2OTB9.kN_Kn6BYebk0WI78ny1VunqZ0-DzOM52QwHwzdmHKZA"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Test 1: Verificar que el token funciona
print("Test 1: Verificar autenticación")
response = requests.get(
    "http://localhost:8000/auth/me",
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"✅ Usuario autenticado: {response.json().get('username')}")
else:
    print(f"❌ Error: {response.text}")
    exit(1)

# Test 2: Verificar que el endpoint existe
print("\nTest 2: Verificar endpoint /search/books")
response2 = requests.get(
    "http://localhost:8000/search/books",
    headers=headers
)
print(f"Status: {response2.status_code}")
print(f"Response: {response2.text[:500]}")

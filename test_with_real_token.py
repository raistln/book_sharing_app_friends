"""
Test del endpoint /search/books usando un token real del navegador.

INSTRUCCIONES:
1. Abre el navegador en http://localhost:3000
2. Abre las DevTools (F12)
3. Ve a la pestaña "Application" o "Storage"
4. En "Local Storage" -> http://localhost:3000
5. Copia el valor de "access_token"
6. Pégalo aquí abajo en la variable TOKEN
"""

import requests

# PEGA TU TOKEN AQUÍ (desde localStorage del navegador)
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0YjdlM2JiYi1lNTMxLTQwODYtYmNhYy05YzUxMjllOGM1MmMiLCJleHAiOjE3NjEwMDA1MTN9.Lyheoo9tvx5E_fe3R2Lthpb-oS-mkw_Gr4KNj8EqCpY"

if TOKEN == "PEGA_TU_TOKEN_AQUI":
    print("❌ ERROR: Necesitas pegar tu token de acceso")
    print("\nPasos:")
    print("1. Abre http://localhost:3000 en el navegador")
    print("2. Presiona F12 para abrir DevTools")
    print("3. Ve a Application -> Local Storage -> http://localhost:3000")
    print("4. Copia el valor de 'access_token'")
    print("5. Pégalo en este script en la variable TOKEN")
    exit(1)

print("=== TEST ENDPOINT /search/books ===")
print(f"Token: {TOKEN[:20]}...")
print()

headers = {"Authorization": f"Bearer {TOKEN}"}

# Test 1: Sin filtros
print("Test 1: Búsqueda sin filtros")
response = requests.get(
    "http://localhost:8000/search/books",
    headers=headers,
    params={
        "page": 1,
        "per_page": 12,
        "sort_by": "created_at",
        "sort_order": "desc"
    }
)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"Tipo de respuesta: {type(data)}")
    print(f"Respuesta: {data}")
    
    # Si es una lista directamente
    if isinstance(data, list):
        print(f"✅ Total items: {len(data)}")
        items = data
    # Si es un objeto con paginación
    else:
        print(f"✅ Total items: {data.get('total', 0)}")
        print(f"✅ Items en página: {len(data.get('items', []))}")
        items = data.get('items', [])
    
    if items:
        print("\n📚 Libros encontrados:")
        for book in items[:5]:  # Solo primeros 5
            print(f"  - '{book['title']}' de {book.get('author', 'N/A')}")
    else:
        print("\n❌ NO SE ENCONTRARON LIBROS")
        print("\nPosibles causas:")
        print("1. No estás en ningún grupo")
        print("2. No hay otros miembros en tus grupos")
        print("3. Los otros miembros no tienen libros activos")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

# Test 2: Con búsqueda de texto
print("\n" + "="*50)
print("Test 2: Búsqueda con texto 'viento'")
response2 = requests.get(
    "http://localhost:8000/search/books",
    headers=headers,
    params={
        "q": "viento",
        "page": 1,
        "per_page": 12
    }
)

print(f"Status: {response2.status_code}")
if response2.status_code == 200:
    data2 = response2.json()
    print(f"✅ Total items: {data2.get('total', 0)}")
    if data2.get('items'):
        print("\n📚 Libros encontrados:")
        for book in data2['items']:
            print(f"  - '{book['title']}' de {book.get('author', 'N/A')}")
    else:
        print("❌ NO SE ENCONTRARON LIBROS CON 'viento'")
else:
    print(f"❌ Error: {response2.status_code}")
    print(response2.text)

import requests
import json

# Simular la petición que hace el frontend
# Usuario: Samsagaz (tulkaspaladin)
# Debería ver libros de Raistln (tulkaspalantus)

# Primero necesitamos el token de Samsagaz
login_data = {
    "username": "Samsagaz",
    "password": "password"  # Asumiendo que es la contraseña por defecto
}

try:
    # Login
    print("=== LOGIN ===")
    login_response = requests.post(
        "http://localhost:8000/auth/login",
        json=login_data
    )
    print(f"Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print(f"Token obtenido: {token[:20]}...")
        
        # Hacer búsqueda
        print("\n=== BÚSQUEDA EN /search/books ===")
        headers = {"Authorization": f"Bearer {token}"}
        search_response = requests.get(
            "http://localhost:8000/search/books",
            headers=headers,
            params={
                "page": 1,
                "per_page": 12,
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        )
        
        print(f"Status: {search_response.status_code}")
        
        if search_response.status_code == 200:
            data = search_response.json()
            print(f"Total items: {data.get('total', 0)}")
            print(f"Items en página: {len(data.get('items', []))}")
            
            if data.get('items'):
                print("\nLibros encontrados:")
                for book in data['items']:
                    print(f"  - '{book['title']}' de {book['author']}")
                    print(f"    Owner ID: {book.get('owner_id')}")
                    print(f"    Archived: {book.get('is_archived')}")
            else:
                print("\n❌ NO SE ENCONTRARON LIBROS")
        else:
            print(f"Error: {search_response.text}")
    else:
        print(f"Error en login: {login_response.text}")
        
except Exception as e:
    print(f"Error: {e}")

"""
Script para reorganizar las rutas de groups.py
Mueve los endpoints /invitations/* ANTES de /{group_id}/invitations
"""

# Leer el archivo
with open('app/api/groups.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar las líneas clave
# Necesitamos mover las líneas 862-1221 ANTES de la línea 661

# Extraer las tres secciones:
# 1. Inicio hasta antes de POST /{group_id}/invitations (líneas 1-660)
# 2. Los endpoints de invitaciones con {group_id} (líneas 661-861)
# 3. Los endpoints de invitaciones sin {group_id} (líneas 862-1221)

section1 = lines[0:660]  # Hasta antes de POST /{group_id}/invitations
section2 = lines[660:861]  # POST y GET /{group_id}/invitations
section3 = lines[861:]  # Resto (invitations sin group_id)

# Reorganizar: section1 + section3 + section2
new_content = section1 + section3 + section2

# Escribir el archivo reorganizado
with open('app/api/groups.py', 'w', encoding='utf-8') as f:
    f.writelines(new_content)

print("✓ Archivo reorganizado exitosamente")
print(f"  - Sección 1 (inicio): {len(section1)} líneas")
print(f"  - Sección 3 (invitations sin group_id): {len(section3)} líneas")  
print(f"  - Sección 2 (invitations con group_id): {len(section2)} líneas")
print(f"  - Total: {len(new_content)} líneas")

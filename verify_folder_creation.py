#!/usr/bin/env python3
"""
Script para verificar la creación de carpetas y listar contenido.
"""

import os
import requests
from dotenv import load_dotenv


def verify_folder_creation():
    """Verifica dónde se creó la carpeta y lista contenido."""
    load_dotenv()
    
    host = os.getenv("SYNOLOGY_IP")
    port = int(os.getenv("SYNOLOGY_PORT", "5000"))
    username = os.getenv("SYNOLOGY_USER")
    password = os.getenv("SYNOLOGY_PASS")
    
    protocol = "https" if port == 5001 else "http"
    base_url = f"{protocol}://{host}:{port}/webapi"
    
    try:
        # 1. Autenticación
        login_url = f"{base_url}/auth.cgi"
        params = {
            "api": "SYNO.API.Auth",
            "version": "3",
            "method": "login",
            "account": username,
            "passwd": password,
            "session": "FileStation",
            "format": "sid"
        }
        
        print("🔐 Autenticando...")
        response = requests.get(login_url, params=params, timeout=30, verify=False)
        data = response.json()
        
        if not data.get("success"):
            print("❌ Error de autenticación")
            return False
        
        sid = data["data"]["sid"]
        print("✅ Autenticación exitosa")
        
        # 2. Listar contenido de /home
        list_url = f"{base_url}/entry.cgi"
        list_params = {
            "api": "SYNO.FileStation.List",
            "version": "2",
            "method": "list",
            "_sid": sid,
            "folder_path": "/home",
            "limit": 100
        }
        
        print("\n📁 Listando contenido de /home...")
        response = requests.get(list_url, params=list_params, timeout=30, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                files = data["data"]["files"]
                print(f"   Encontrados {len(files)} elementos en /home:")
                
                if not files:
                    print("   (directorio vacío)")
                else:
                    for file in files:
                        file_type = "📁" if file["isdir"] else "📄"
                        name = file['name']
                        size = f" ({file['additional']['size']} bytes)" if not file["isdir"] else ""
                        print(f"   {file_type} {name}{size}")
            else:
                error = data.get('error', {})
                print(f"   ❌ Error al listar: {error.get('code', 'N/A')}")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
        
        # 3. Verificar si existe la carpeta específica
        print(f"\n🔍 Verificando si existe /home/test_upload_folder...")
        check_params = {
            "api": "SYNO.FileStation.List",
            "version": "2",
            "method": "list",
            "_sid": sid,
            "folder_path": "/home/test_upload_folder",
            "limit": 10
        }
        
        response = requests.get(list_url, params=check_params, timeout=30, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("   ✅ La carpeta /home/test_upload_folder existe")
                files = data["data"]["files"]
                print(f"   Contiene {len(files)} elementos")
            else:
                error = data.get('error', {})
                print(f"   ❌ La carpeta no existe o no es accesible: {error.get('code', 'N/A')}")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
        
        # 4. Probar crear carpeta con nombre diferente
        print(f"\n📁 Creando carpeta de prueba con timestamp...")
        import time
        timestamp = int(time.time())
        folder_name = f"test_folder_{timestamp}"
        
        create_params = {
            "api": "SYNO.FileStation.CreateFolder",
            "version": "2",
            "method": "create",
            "_sid": sid,
            "folder_path": "/home",
            "name": folder_name
        }
        
        response = requests.get(list_url, params=create_params, timeout=30, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✅ Carpeta {folder_name} creada exitosamente")
                
                # Verificar que aparece en el listado
                print(f"\n🔍 Verificando que aparece en el listado...")
                response = requests.get(list_url, params=list_params, timeout=30, verify=False)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        files = data["data"]["files"]
                        folder_found = any(f["name"] == folder_name for f in files)
                        if folder_found:
                            print(f"   ✅ La carpeta {folder_name} aparece en el listado")
                        else:
                            print(f"   ❌ La carpeta {folder_name} NO aparece en el listado")
            else:
                error = data.get('error', {})
                print(f"   ❌ Error al crear carpeta: {error.get('code', 'N/A')}")
        else:
            print(f"   ❌ Error HTTP al crear carpeta: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=== VERIFICACIÓN DE CREACIÓN DE CARPETAS ===\n")
    verify_folder_creation() 
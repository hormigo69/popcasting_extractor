#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la configuración del NAS Synology.
"""

import os
import sys
from synology_client import SynologyClient


def test_synology_connection():
    """Prueba la conexión básica al NAS."""
    print("🔍 DIAGNÓSTICO DE CONEXIÓN SYNOLOGY")
    print("=" * 50)
    
    try:
        # Verificar variables de entorno
        print("📋 Verificando configuración:")
        host = os.getenv("SYNOLOGY_IP")
        port = os.getenv("SYNOLOGY_PORT")
        user = os.getenv("SYNOLOGY_USER")
        pass_env = os.getenv("SYNOLOGY_PASS")
        
        print(f"  Host: {host}")
        print(f"  Puerto: {port}")
        print(f"  Usuario: {user}")
        print(f"  Contraseña: {'*' * len(pass_env) if pass_env else 'NO CONFIGURADA'}")
        
        if not all([host, user, pass_env]):
            print("❌ Faltan variables de entorno. Configura SYNOLOGY_IP, SYNOLOGY_USER y SYNOLOGY_PASS")
            return False
        
        # Crear cliente
        print("\n🔌 Conectando al NAS...")
        synology = SynologyClient()
        
        # Probar login
        if not synology.login():
            print("❌ Error en la autenticación")
            return False
        
        print("✅ Autenticación exitosa")
        
        # Probar listar carpeta raíz
        print("\n📁 Probando listar carpeta raíz...")
        try:
            files = synology.list_files("/")
            if files is not None:
                print("✅ Listado de archivos exitoso")
            else:
                print("❌ Error al listar archivos")
        except Exception as e:
            print(f"❌ Error al listar archivos: {e}")
        
        # Probar crear carpeta de prueba
        print("\n📁 Probando crear carpeta de prueba...")
        try:
            if synology.create_folder("/test_folder"):
                print("✅ Creación de carpeta exitosa")
            else:
                print("❌ Error al crear carpeta")
        except Exception as e:
            print(f"❌ Error al crear carpeta: {e}")
        
        # Probar subir archivo pequeño
        print("\n📤 Probando subida de archivo pequeño...")
        try:
            # Crear archivo de prueba
            test_file = "test_upload.txt"
            with open(test_file, 'w') as f:
                f.write("Archivo de prueba para Synology")
            
            if synology.upload_file(test_file, "/"):
                print("✅ Subida de archivo exitosa")
            else:
                print("❌ Error al subir archivo")
            
            # Limpiar archivo de prueba
            os.remove(test_file)
        except Exception as e:
            print(f"❌ Error al subir archivo: {e}")
        
        # Cerrar sesión
        synology.logout()
        
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False


def check_synology_api_info():
    """Verifica información de la API del NAS."""
    print("\n🔧 INFORMACIÓN DE LA API SYNOLOGY")
    print("=" * 50)
    
    try:
        synology = SynologyClient()
        
        # Obtener información de la API
        api_url = f"{synology.base_url}/query.cgi"
        params = {
            'api': 'SYNO.API.Info',
            'version': '1',
            'method': 'query',
            'query': 'SYNO.FileStation'
        }
        
        import requests
        response = requests.get(api_url, params=params, verify=False, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Información de API obtenida:")
            print(f"  Respuesta: {data}")
        else:
            print(f"❌ Error al obtener información de API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error al verificar API: {e}")


if __name__ == "__main__":
    test_synology_connection()
    check_synology_api_info() 
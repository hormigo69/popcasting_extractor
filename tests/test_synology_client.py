#!/usr/bin/env python3
"""
Script de prueba para la clase SynologyClient.
"""

from synology_client import SynologyClient


def test_synology_client():
    """Prueba la clase SynologyClient."""
    print("=== PRUEBA DE SYNOLOGY CLIENT ===\n")
    
    try:
        # Crear cliente
        client = SynologyClient()
        print("✅ Cliente creado correctamente")
        
        # 1. Login
        if not client.login():
            print("❌ Error en login")
            return False
        
        # 2. Listar archivos en /popcasting_marilyn (carpeta actual)
        print("\n📋 Listando archivos en /popcasting_marilyn:")
        files = client.list_files("/popcasting_marilyn")
        
        # 3. Crear carpeta /popcasting_marilyn/mp3
        print("\n📁 Creando carpeta /popcasting_marilyn/mp3:")
        folder_created = client.create_folder("/popcasting_marilyn/mp3")
        
        if folder_created:
            # 4. Subir archivo a /popcasting_marilyn/mp3
            print("\n📤 Probando subida a /popcasting_marilyn/mp3:")
            success = client.upload_file("data/Especiales.json", "/popcasting_marilyn/mp3")
        else:
            print("❌ No se pudo crear la carpeta /mp3")
            success = False
        
        if success:
            # 5. Listar archivos en /popcasting_marilyn/mp3 para verificar
            print("\n📋 Verificando archivos en /popcasting_marilyn/mp3:")
            mp3_files = client.list_files("/popcasting_marilyn/mp3")
            
            if mp3_files:
                print("✅ Archivo subido y verificado correctamente")
            else:
                print("⚠️ Archivo subido pero no se puede verificar")
        else:
            print("❌ Error en la subida")
        
        # 5. Logout
        client.logout()
        
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_context_manager():
    """Prueba el uso de la clase como context manager."""
    print("\n=== PRUEBA DE CONTEXT MANAGER ===\n")
    
    try:
        with SynologyClient() as client:
            print("✅ Context manager funciona correctamente")
            
            # Listar archivos
            files = client.list_files("/popcasting_marilyn")
            
            # Crear carpeta si no existe
            client.create_folder("/popcasting_marilyn/mp3")
            
            # Subir otro archivo de prueba
            success = client.upload_file("data/Especiales.json", "/popcasting_marilyn/mp3")
            
            if success:
                print("✅ Subida exitosa con context manager")
                return True
            else:
                print("❌ Error en subida con context manager")
                return False
                
    except Exception as e:
        print(f"❌ Error con context manager: {e}")
        return False


if __name__ == "__main__":
    # Prueba 1: Uso manual
    success1 = test_synology_client()
    
    # Prueba 2: Context manager
    success2 = test_context_manager()
    
    print("\n" + "="*50)
    if success1 and success2:
        print("🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("✅ La clase SynologyClient está lista para usar")
    else:
        print("❌ Algunas pruebas fallaron")
        print("⚠️ Revisa la configuración y permisos") 
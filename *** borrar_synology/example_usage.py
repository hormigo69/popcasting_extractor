#!/usr/bin/env python3
"""
Ejemplo de uso de la clase SynologyClient.
"""

from synology_client import SynologyClient


def example_usage():
    """Ejemplo de uso de la clase SynologyClient."""
    print("=== EJEMPLO DE USO SYNOLOGY CLIENT ===\n")
    
    # Ejemplo 1: Uso manual
    print("📋 Ejemplo 1: Uso manual")
    print("-" * 40)
    
    client = SynologyClient()
    
    if client.login():
        # Listar archivos
        files = client.list_files("/popcasting_marilyn")
        
        # Crear carpeta mp3 si no existe
        client.create_folder("/popcasting_marilyn/mp3")
        
        # Subir archivo
        success = client.upload_file("data/Especiales.json", "/popcasting_marilyn/mp3")
        
        if success:
            # Verificar subida
            mp3_files = client.list_files("/popcasting_marilyn/mp3")
            print("✅ Archivo subido correctamente")
        
        client.logout()
    
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 2: Uso con context manager (recomendado)
    print("📋 Ejemplo 2: Context manager")
    print("-" * 40)
    
    try:
        with SynologyClient() as client:
            # Listar archivos
            files = client.list_files("/popcasting_marilyn")
            
            # Crear carpeta y subir archivo
            client.create_folder("/popcasting_marilyn/mp3")
            success = client.upload_file("data/Especiales.json", "/popcasting_marilyn/mp3")
            
            if success:
                print("✅ Archivo subido con context manager")
                
                # Listar archivos en mp3
                mp3_files = client.list_files("/popcasting_marilyn/mp3")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50)
    print("🎉 Ejemplos completados")


if __name__ == "__main__":
    example_usage() 
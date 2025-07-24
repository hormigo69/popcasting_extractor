#!/usr/bin/env python3
"""
Cliente de línea de comandos para subir archivos a Synology NAS
utilizando la API de File Station.
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
import argparse


class SynologyUploader:
    """Cliente para subir archivos a Synology NAS usando la API de File Station."""
    
    def __init__(self, host, port, username, password):
        """
        Inicializa el cliente de Synology.
        
        Args:
            host (str): Dirección IP del NAS
            port (int): Puerto del NAS (normalmente 5000 o 5001 para HTTPS)
            username (str): Nombre de usuario
            password (str): Contraseña
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sid = None
        # Usar HTTPS para puerto 5001, HTTP para otros puertos
        protocol = "https" if port == 5001 else "http"
        self.base_url = f"{protocol}://{host}:{port}/webapi"
        
    def login(self):
        """
        Autentica con el NAS y obtiene un SID (Session ID).
        
        Returns:
            bool: True si la autenticación fue exitosa, False en caso contrario
        """
        try:
            login_url = f"{self.base_url}/auth.cgi"
            params = {
                "api": "SYNO.API.Auth",
                "version": "3",
                "method": "login",
                "account": self.username,
                "passwd": self.password,
                "session": "FileStation",
                "format": "sid"
            }
            
            response = requests.get(login_url, params=params, timeout=30, verify=False)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("success"):
                self.sid = data["data"]["sid"]
                print(f"✅ Autenticación exitosa. SID obtenido: {self.sid[:10]}...")
                return True
            else:
                print(f"❌ Error de autenticación: {data.get('error', {}).get('code', 'Desconocido')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado durante la autenticación: {e}")
            return False
    
    def upload_file(self, local_file_path, remote_path="/"):
        """
        Sube un archivo al NAS.
        
        Args:
            local_file_path (str): Ruta del archivo local a subir
            remote_path (str): Ruta de destino en el NAS
            
        Returns:
            bool: True si la subida fue exitosa, False en caso contrario
        """
        if not self.sid:
            print("❌ No hay sesión activa. Ejecuta login() primero.")
            return False
            
        if not os.path.exists(local_file_path):
            print(f"❌ El archivo local no existe: {local_file_path}")
            return False
            
        try:
            upload_url = f"{self.base_url}/entry.cgi"
            
            # Parámetros para la API de File Station
            params = {
                "api": "SYNO.FileStation.Upload",
                "version": "2",
                "method": "upload",
                "_sid": self.sid,
                "path": remote_path,
                "create_parents": "true",
                "overwrite": "true"
            }
            
            # Preparar el archivo para subir
            with open(local_file_path, 'rb') as file:
                files = {'file': (os.path.basename(local_file_path), file, 'application/octet-stream')}
                
                print(f"📤 Subiendo {local_file_path} a {remote_path}...")
                response = requests.post(upload_url, params=params, files=files, timeout=120, verify=False)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("success"):
                    print(f"✅ Archivo subido exitosamente")
                    return True
                else:
                    print(f"❌ Error al subir archivo: {data.get('error', {}).get('code', 'Desconocido')}")
                    return False
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión durante la subida: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado durante la subida: {e}")
            return False
    
    def logout(self):
        """
        Cierra la sesión en el NAS.
        
        Returns:
            bool: True si el cierre de sesión fue exitoso, False en caso contrario
        """
        if not self.sid:
            print("ℹ️ No hay sesión activa para cerrar.")
            return True
            
        try:
            logout_url = f"{self.base_url}/auth.cgi"
            params = {
                "api": "SYNO.API.Auth",
                "version": "3",
                "method": "logout",
                "session": "FileStation",
                "_sid": self.sid
            }
            
            response = requests.get(logout_url, params=params, timeout=30, verify=False)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("success"):
                print("✅ Sesión cerrada exitosamente")
                self.sid = None
                return True
            else:
                print(f"⚠️ Error al cerrar sesión: {data.get('error', {}).get('code', 'Desconocido')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error de conexión al cerrar sesión: {e}")
            return False
        except Exception as e:
            print(f"⚠️ Error inesperado al cerrar sesión: {e}")
            return False


def main():
    """Función principal del programa."""
    parser = argparse.ArgumentParser(
        description="Cliente para subir archivos a Synology NAS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python synology_uploader.py data/Especiales.json
  python synology_uploader.py --remote-path "/backup" data/Especiales.json
        """
    )
    
    parser.add_argument(
        "file_path",
        help="Ruta del archivo local a subir"
    )
    
    parser.add_argument(
        "--remote-path",
        default="/",
        help="Ruta de destino en el NAS (por defecto: /)"
    )
    
    parser.add_argument(
        "--host",
        help="Dirección IP del NAS (sobrescribe la configuración del .env)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        help="Puerto del NAS (sobrescribe la configuración del .env)"
    )
    
    args = parser.parse_args()
    
    # Cargar configuración desde .env
    load_dotenv()
    
    # Obtener configuración (args tienen prioridad sobre .env)
    host = args.host or os.getenv("SYNOLOGY_IP") or os.getenv("SYNOLOGY_HOST")
    port = args.port or int(os.getenv("SYNOLOGY_PORT", "5000"))
    username = os.getenv("SYNOLOGY_USER")
    password = os.getenv("SYNOLOGY_PASS")
    
    # Validar configuración
    if not all([host, username, password]):
        print("❌ Configuración incompleta. Asegúrate de que tu archivo .env contenga:")
        print("   SYNOLOGY_IP=tu_ip_del_nas")
        print("   SYNOLOGY_PORT=5000")
        print("   SYNOLOGY_USER=tu_usuario")
        print("   SYNOLOGY_PASS=tu_contraseña")
        sys.exit(1)
    
    # Validar que el archivo existe
    if not os.path.exists(args.file_path):
        print(f"❌ El archivo no existe: {args.file_path}")
        sys.exit(1)
    
    # Crear cliente y ejecutar operaciones
    uploader = SynologyUploader(host, port, username, password)
    
    try:
        # 1. Autenticación
        if not uploader.login():
            sys.exit(1)
        
        # 2. Subida del archivo
        if not uploader.upload_file(args.file_path, args.remote_path):
            sys.exit(1)
        
        # 3. Cierre de sesión
        uploader.logout()
        
        print("🎉 Operación completada exitosamente")
        
    except KeyboardInterrupt:
        print("\n⚠️ Operación cancelada por el usuario")
        uploader.logout()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        uploader.logout()
        sys.exit(1)


if __name__ == "__main__":
    main() 
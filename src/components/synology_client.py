#!/usr/bin/env python3
"""
Cliente reutilizable para Synology NAS.
"""

import requests
import os
from dotenv import load_dotenv

# Deshabilitar warnings de SSL
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


class SynologyClient:
    """Cliente para interactuar con Synology NAS."""
    
    def __init__(self, host=None, port=None, username=None, password=None):
        """
        Inicializa el cliente.
        
        Args:
            host: IP del NAS (por defecto desde .env)
            port: Puerto del NAS (por defecto desde .env)
            username: Usuario (por defecto desde .env)
            password: Contraseña (por defecto desde .env)
        """
        load_dotenv()
        
        self.host = host or os.getenv("SYNOLOGY_IP")
        self.port = port or int(os.getenv("SYNOLOGY_PORT", "5000"))
        self.username = username or os.getenv("SYNOLOGY_USER")
        self.password = password or os.getenv("SYNOLOGY_PASS")
        self.sid = None
        
        if not all([self.host, self.username, self.password]):
            raise ValueError("Faltan datos de conexión. Configura SYNOLOGY_IP, SYNOLOGY_USER y SYNOLOGY_PASS en .env")
        
        protocol = 'https' if self.port == 5001 else 'http'
        self.base_url = f"{protocol}://{self.host}:{self.port}/webapi"
    
    def login(self):
        """
        Autentica con el NAS y obtiene SID.
        
        Returns:
            bool: True si la autenticación fue exitosa
        """
        auth_url = f"{self.base_url}/auth.cgi"
        params = {
            'api': 'SYNO.API.Auth',
            'version': '7',
            'method': 'login',
            'account': self.username,
            'passwd': self.password,
            'session': 'FileStation',
            'format': 'sid'
        }
        
        try:
            response = requests.get(auth_url, params=params, verify=False, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                self.sid = data['data']['sid']
                print(f"✅ Autenticación exitosa con {self.host}")
                return True
            else:
                error_code = data.get('error', {}).get('code')
                print(f"❌ Error de autenticación (código {error_code})")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def logout(self):
        """Cierra la sesión."""
        if not self.sid:
            return
        
        logout_url = f"{self.base_url}/auth.cgi"
        params = {
            'api': 'SYNO.API.Auth',
            'version': '1',
            'method': 'logout',
            'session': 'FileStation',
            '_sid': self.sid
        }
        
        try:
            requests.get(logout_url, params=params, verify=False, timeout=10)
            print("✅ Sesión cerrada")
        except requests.exceptions.RequestException:
            pass
        finally:
            self.sid = None
    
    def upload_file(self, local_file_path, remote_folder="/mp3"):
        """
        Sube un archivo al NAS.
        
        Args:
            local_file_path: Ruta del archivo local
            remote_folder: Carpeta de destino en el NAS (por defecto /mp3)
            
        Returns:
            bool: True si la subida fue exitosa
        """
        if not self.sid:
            print("❌ No hay sesión activa. Ejecuta login() primero.")
            return False
        
        if not os.path.exists(local_file_path):
            print(f"❌ El archivo local no existe: {local_file_path}")
            return False
        
        upload_url = f"{self.base_url}/entry.cgi"
        params = {
            'api': 'SYNO.FileStation.Upload',
            'version': '2',
            'method': 'upload',
            '_sid': self.sid
        }
        data = {
            'path': remote_folder,
            'create_parents': 'true'
        }
        
        try:
            files = {'file': (os.path.basename(local_file_path), open(local_file_path, 'rb'))}
            print(f"📤 Subiendo {os.path.basename(local_file_path)} a {remote_folder}...")
            
            response = requests.post(upload_url, params=params, data=data, files=files, verify=False, timeout=120)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                print(f"✅ Archivo subido exitosamente a {remote_folder}")
                return True
            else:
                error_code = result.get('error', {}).get('code')
                print(f"❌ Error al subir archivo (código {error_code})")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en la subida: {e}")
            return False
        finally:
            if 'files' in locals():
                files['file'][1].close()
    
    def file_exists(self, remote_file_path: str) -> bool:
        """
        Comprueba si un archivo existe en el NAS usando el método getinfo de la API.
        Args:
            remote_file_path: Ruta completa del archivo en el NAS (ej: /popcasting_marilyn/mp3/popcasting_0485.mp3)
        Returns:
            bool: True si el archivo existe, False si no existe o hay error
        """
        if not self.sid:
            print("❌ No hay sesión activa. Ejecuta login() primero.")
            return False
        getinfo_url = f"{self.base_url}/entry.cgi"
        params = {
            'api': 'SYNO.FileStation.List',
            'version': '2',
            'method': 'getinfo',
            '_sid': self.sid,
            'path': f'["{remote_file_path}"]',
            'additional': 'size,time,owner,perm,type'
        }
        try:
            response = requests.get(getinfo_url, params=params, verify=False, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Verificar si la respuesta es exitosa y no hay errores
            if data.get('success') and data.get('data', {}).get('files'):
                files = data['data']['files']
                # Si hay archivos y ninguno tiene código de error, el archivo existe
                for file_info in files:
                    if file_info.get('code') == 408:  # File not found
                        return False
                return True
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error comprobando existencia de archivo: {e}")
            return False

    def list_files(self, remote_folder="/mp3"):
        """
        Lista archivos en una carpeta.
        Args:
            remote_folder: Carpeta a listar (por defecto /mp3)
        Returns:
            list: Lista de archivos o None si hay error
        """
        if not self.sid:
            print("❌ No hay sesión activa. Ejecuta login() primero.")
            return None
        list_url = f"{self.base_url}/entry.cgi"
        params = {
            'api': 'SYNO.FileStation.List',
            'version': '2',
            'method': 'list',
            '_sid': self.sid,
            'folder_path': remote_folder,
            'limit': 1000,  # Aumentar el límite para obtener más archivos
            'additional': 'size,time,owner,perm,type'
        }
        try:
            response = requests.get(list_url, params=params, verify=False, timeout=30)
            response.raise_for_status()
            data = response.json()
            if data.get('success'):
                files = data['data']['files']
                # Eliminado el print masivo para evitar logs innecesarios
                return files
            else:
                error_code = data.get('error', {}).get('code')
                print(f"❌ Error al listar archivos (código {error_code})")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al listar archivos: {e}")
            return None
    
    def create_folder(self, folder_path):
        """
        Crea una carpeta en el NAS.
        
        Args:
            folder_path: Ruta de la carpeta a crear
            
        Returns:
            bool: True si la carpeta se creó exitosamente
        """
        if not self.sid:
            print("❌ No hay sesión activa. Ejecuta login() primero.")
            return False
        
        create_url = f"{self.base_url}/entry.cgi"
        params = {
            'api': 'SYNO.FileStation.CreateFolder',
            'version': '2',
            'method': 'create',
            '_sid': self.sid,
            'folder_path': os.path.dirname(folder_path),
            'name': os.path.basename(folder_path)
        }
        
        try:
            print(f"📁 Creando carpeta {folder_path}...")
            response = requests.get(create_url, params=params, verify=False, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                print(f"✅ Carpeta {folder_path} creada exitosamente")
                return True
            else:
                error_code = data.get('error', {}).get('code')
                print(f"❌ Error al crear carpeta (código {error_code})")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al crear carpeta: {e}")
            return False

    def download_file(self, remote_file_path, local_folder="downloads"):
        """
        Descarga un archivo del NAS.
        
        Args:
            remote_file_path: Ruta del archivo en el NAS
            local_folder: Carpeta local de destino
            
        Returns:
            bool: True si la descarga fue exitosa
        """
        if not self.sid:
            print("❌ No hay sesión activa. Ejecuta login() primero.")
            return False
        
        # Crear carpeta local si no existe
        os.makedirs(local_folder, exist_ok=True)
        
        download_url = f"{self.base_url}/entry.cgi"
        params = {
            'api': 'SYNO.FileStation.Download',
            'version': '2',
            'method': 'download',
            '_sid': self.sid,
            'path': remote_file_path
        }
        
        try:
            print(f"📥 Descargando {os.path.basename(remote_file_path)}...")
            response = requests.get(download_url, params=params, verify=False, timeout=60, stream=True)
            response.raise_for_status()
            
            local_file_path = os.path.join(local_folder, os.path.basename(remote_file_path))
            with open(local_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Archivo descargado a {local_file_path}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en la descarga: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        if not self.login():
            raise Exception("No se pudo autenticar con el NAS")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.logout() 
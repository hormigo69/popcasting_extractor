import requests
import os
import logging

logger = logging.getLogger(__name__)

class SynologyClient:
    """Cliente simplificado para la API File Station de Synology NAS."""
    
    def __init__(self, ip, port, username, password):
        self.base_url = f"http://{ip}:{port}/webapi"
        self.username = username
        self.password = password
        self.sid = None
        logger.info(f"Cliente Synology inicializado para {ip}:{port}")
    
    def login(self):
        """Autentica con el NAS y obtiene el token de sesión."""
        try:
            params = {
                "api": "SYNO.API.Auth",
                "version": "3",
                "method": "login",
                "account": self.username,
                "passwd": self.password,
                "session": "FileStation",
                "format": "sid"
            }
            
            response = requests.get(f"{self.base_url}/auth.cgi", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get("success"):
                self.sid = data["data"]["sid"]
                logger.info("Login exitoso en Synology NAS")
                return True
            else:
                logger.error(f"Error en login: {data.get('error', {}).get('code')}")
                return False
                
        except Exception as e:
            logger.error(f"Error de conexión durante login: {e}")
            return False
    
    def logout(self):
        """Cierra la sesión en el NAS."""
        if not self.sid:
            return True
            
        try:
            params = {
                "api": "SYNO.API.Auth",
                "version": "3",
                "method": "logout",
                "session": "FileStation",
                "_sid": self.sid
            }
            
            response = requests.get(f"{self.base_url}/auth.cgi", params=params, timeout=30)
            response.raise_for_status()
            
            if response.json().get("success"):
                logger.info("Logout exitoso de Synology NAS")
                self.sid = None
                return True
            return False
                
        except Exception as e:
            logger.error(f"Error durante logout: {e}")
            return False
    
    def upload_file(self, local_path: str, remote_folder_path: str) -> bool:
        """Sube un archivo local a una carpeta específica en el NAS."""
        if not self.sid:
            logger.error("No se ha iniciado sesión.")
            return False

        if not os.path.exists(local_path):
            logger.error(f"El archivo local '{local_path}' no existe.")
            return False

        url_params = {
            'api': 'SYNO.FileStation.Upload',
            'version': 2,
            'method': 'upload',
            '_sid': self.sid
        }

        multipart_data = {
            'path': (None, remote_folder_path),
            'create_parents': (None, 'true'),
            'overwrite': (None, 'true'),
            'file': (os.path.basename(local_path), open(local_path, 'rb'), 'application/octet-stream')
        }
        
        try:
            response = requests.post(f"{self.base_url}/entry.cgi", params=url_params, files=multipart_data, timeout=300)
            response.raise_for_status()

            data = response.json()
            if data.get('success'):
                logger.info(f"✅ Archivo '{local_path}' subido con éxito.")
                return True
            else:
                logger.error(f"❌ Fallo en la subida. Código: {data.get('error', {}).get('code')}")
                return False

        except Exception as e:
            logger.error(f"❌ Error durante la subida: {e}")
            return False
        finally:
            multipart_data['file'][1].close()
    
    def list_files(self, folder_path="/"):
        """Lista archivos y carpetas en una ruta específica del NAS."""
        if not self.sid:
            logger.error("No se ha iniciado sesión.")
            return None
            
        try:
            params = {
                "api": "SYNO.FileStation.List",
                "version": "2",
                "method": "list",
                "folder_path": folder_path,
                "_sid": self.sid
            }
            
            response = requests.get(f"{self.base_url}/entry.cgi", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get("success"):
                files = data.get("data", {}).get("files", [])
                logger.info(f"Encontrados {len(files)} elementos en {folder_path}")
                return files
            else:
                logger.error(f"Error al listar archivos: {data.get('error', {}).get('code')}")
                return None
                
        except Exception as e:
            logger.error(f"Error al listar archivos: {e}")
            return None

    def read_file(self, file_path):
        """Lee el contenido de un archivo del NAS."""
        if not self.sid:
            logger.error("No se ha iniciado sesión.")
            return None
            
        try:
            params = {
                "api": "SYNO.FileStation.Download",
                "version": "2",
                "method": "download",
                "path": file_path,
                "_sid": self.sid
            }
            
            response = requests.get(f"{self.base_url}/entry.cgi", params=params, timeout=30)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                data = response.json()
                logger.error(f"Error al leer archivo: {data.get('error', {}).get('code')}")
                return None
            else:
                content = response.text
                logger.info(f"Archivo leído exitosamente, {len(content)} caracteres")
                return content
                
        except Exception as e:
            logger.error(f"Error al leer archivo: {e}")
            return None

    def list_shared_folders(self) -> list:
        """Devuelve una lista de carpetas compartidas accesibles."""
        if not self.sid:
            logger.error("No se ha iniciado sesión.")
            return []

        try:
            params = {
                'api': 'SYNO.FileStation.List',
                'version': 1,
                'method': 'list_share',
                '_sid': self.sid
            }
            
            response = requests.get(f"{self.base_url}/entry.cgi", params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('success'):
                return data.get('data', {}).get('shares', [])
            else:
                logger.error(f"Error al listar carpetas compartidas: {data}")
                return []
        except Exception as e:
            logger.error(f"Error al listar carpetas compartidas: {e}")
            return []

    def __enter__(self):
        """Context manager entry point."""
        if not self.login():
            raise Exception("No se pudo autenticar con Synology NAS")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.logout()


if __name__ == '__main__':
    import os, sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.components.config_manager import ConfigManager
    from src.utils.logger import logger
    
    logger.info("=== PRUEBA SIMPLIFICADA DE SYNOLOGY CLIENT ===")
    try:
        cfg = ConfigManager()
        credentials = cfg.get_synology_credentials()
        
        # Crear archivo de prueba
        test_filename = "test_simple.txt"
        test_content = "Prueba simplificada del cliente Synology\nFecha: 2025-01-27"
        
        with open(test_filename, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        logger.info(f"Archivo de prueba creado: {test_filename}")
        
        with SynologyClient(
            ip=credentials["ip"],
            port=credentials["port"],
            username=credentials["user"],
            password=credentials["password"]
        ) as client:
            # Listar carpetas compartidas
            shared_folders = client.list_shared_folders()
            logger.info("Carpetas compartidas disponibles:")
            for folder in shared_folders:
                logger.info(f"  -> {folder.get('name')}: {folder.get('path')}")
            
            # Buscar popcasting_marilyn
            popcasting_folder = next((f for f in shared_folders if f.get('name') == 'popcasting_marilyn'), None)
            
            if popcasting_folder:
                # Subir archivo
                success = client.upload_file(test_filename, popcasting_folder.get('path'))
                
                if success:
                    # Verificar subida
                    files = client.list_files(popcasting_folder.get('path'))
                    if files:
                        logger.info("Contenido de la carpeta:")
                        for file_info in files:
                            name = file_info.get("name", "Sin nombre")
                            is_dir = file_info.get("isdir", False)
                            logger.info(f"  {'📁' if is_dir else '📄'} {name}")
                            
                            # Leer archivo subido
                            if name == test_filename:
                                content = client.read_file(f"{popcasting_folder.get('path')}/{name}")
                                if content:
                                    logger.info(f"✅ Contenido verificado: {content.strip()}")
            else:
                logger.error("No se encontró la carpeta popcasting_marilyn")
        
        # Limpiar
        if os.path.exists(test_filename):
            os.remove(test_filename)
            logger.info(f"Archivo de prueba eliminado: {test_filename}")
            
    except Exception as e:
        logger.error(f"❌ ERROR: {e}") 
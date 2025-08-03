import configparser
import os
from pathlib import Path
from dotenv import load_dotenv
import sys

# Agregar el directorio src al path para importaciones
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

class ConfigManager:
    """
    Gestiona la lectura de configuraciones y carga secretos desde variables de entorno.
    """
    def __init__(self, config_path=None, env_path=None):
        # Buscar automáticamente los archivos de configuración
        if config_path is None:
            # Buscar config.ini en la carpeta sincronizador_rss
            current_dir = Path(__file__).parent.parent.parent
            config_path = current_dir / "config.ini"
        
        self.config = configparser.ConfigParser()
        if not self.config.read(config_path):
            raise FileNotFoundError(f"El archivo de configuración '{config_path}' no se encontró.")
        
        # Cargar variables de entorno desde .env
        # load_dotenv() buscará automáticamente el archivo .env en el directorio de trabajo actual
        load_dotenv()

    def get_supabase_credentials(self):
        """
        Obtiene las credenciales para la API de Supabase desde las variables de entorno.
        """
        url = os.getenv("supabase_project_url")
        key = os.getenv("supabase_service_role") or os.getenv("supabase_api_key")
        
        if not all([url, key]):
            raise ValueError("Faltan las variables de entorno supabase_project_url o supabase_service_role.")
            
        return {"url": url, "key": key}

    def get_synology_credentials(self):
        """
        Obtiene las credenciales para Synology NAS desde las variables de entorno.
        """
        ip = os.getenv("SYNOLOGY_IP")
        port = os.getenv("SYNOLOGY_PORT")
        user = os.getenv("SYNOLOGY_USER")
        password = os.getenv("SYNOLOGY_PASS")
        shared_folder = os.getenv("SYNOLOGY_SHARED_FOLDER")
        
        if not all([ip, port, user, password, shared_folder]):
            raise ValueError("Faltan las variables de entorno SYNOLOGY_IP, SYNOLOGY_PORT, SYNOLOGY_USER, SYNOLOGY_PASS o SYNOLOGY_SHARED_FOLDER.")
            
        return {
            "ip": ip,
            "port": port,
            "user": user,
            "password": password,
            "shared_folder": shared_folder
        }

    def get_rss_url(self):
        """Devuelve la URL del feed RSS."""
        return self.config['rss']['url']

    def get_wordpress_config(self):
        """Devuelve la configuración de WordPress."""
        base_url = self.config['wordpress']['url']
        api_url = f"{base_url.rstrip('/')}/wp-json/wp/v2"
        return {'api_url': api_url} 
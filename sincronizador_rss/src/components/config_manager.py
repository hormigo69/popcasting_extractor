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
        
        if env_path is None:
            # Buscar .env en el raíz del proyecto (un nivel arriba)
            current_dir = Path(__file__).parent.parent.parent
            env_path = current_dir.parent / ".env"
        
        self.config = configparser.ConfigParser()
        if not self.config.read(config_path):
            raise FileNotFoundError(f"El archivo de configuración '{config_path}' no se encontró.")
        
        if os.path.exists(env_path):
            load_dotenv(dotenv_path=env_path)

    def get_supabase_credentials(self):
        """
        Obtiene las credenciales para la API de Supabase desde las variables de entorno.
        """
        url = os.getenv("supabase_project_url")
        key = os.getenv("supabase_api_key")
        
        if not all([url, key]):
            raise ValueError("Faltan las variables de entorno supabase_project_url o supabase_api_key.")
            
        return {"url": url, "key": key}

    def get_rss_url(self):
        """Devuelve la URL del feed RSS."""
        return self.config['rss']['url']

    def get_wordpress_config(self):
        """Devuelve la configuración de WordPress."""
        base_url = self.config['wordpress']['url']
        api_url = f"{base_url.rstrip('/')}/wp-json/wp/v2"
        return {'api_url': api_url} 
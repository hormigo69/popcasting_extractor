"""
Gestor de configuración para el extractor de Popcasting.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class ConfigManager:
    """
    Gestiona la lectura de configuraciones y carga secretos desde variables de entorno.
    """
    
    def __init__(self):
        """Inicializa el gestor de configuración."""
        pass

    def get_synology_credentials(self):
        """
        Obtiene las credenciales para Synology NAS desde las variables de entorno.
        """
        ip = os.getenv("SYNOLOGY_IP")
        port = os.getenv("SYNOLOGY_PORT", "5000")
        user = os.getenv("SYNOLOGY_USER")
        password = os.getenv("SYNOLOGY_PASS")
        
        if not all([ip, user, password]):
            raise ValueError("Faltan las variables de entorno SYNOLOGY_IP, SYNOLOGY_USER o SYNOLOGY_PASS.")
            
        return {
            "host": ip,
            "port": int(port),
            "username": user,
            "password": password
        } 
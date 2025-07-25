# Gestor de base de datos para el sincronizador RSS
from supabase import create_client, Client
import logging


class DatabaseManager:
    """Gestor de base de datos Supabase para el sincronizador RSS."""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """Inicializa la conexión a Supabase."""
        self.logger = logging.getLogger(__name__)
        
        try:
            # Crear cliente de Supabase
            self.client: Client = create_client(supabase_url, supabase_key)
            self.logger.info("✅ Conexión a Supabase establecida correctamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error al conectar a Supabase: {e}")
            raise
    
    def test_connection(self):
        """Prueba la conexión ejecutando una consulta simple."""
        try:
            # Intentar hacer una consulta simple para verificar la conexión
            result = self.client.table("podcasts").select("id").limit(1).execute()
            self.logger.info("✅ Prueba de conexión a Supabase exitosa")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error en prueba de conexión: {e}")
            raise
    
    def close(self):
        """Cierra la conexión a Supabase."""
        # La librería de Supabase maneja automáticamente las conexiones
        self.logger.info("🔒 Conexión a Supabase cerrada")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def test_database_connection():
    """
    Función de prueba para verificar la conexión a la base de datos.
    Se ejecuta cuando se llama directamente este archivo.
    """
    import sys
    import os
    
    # Agregar el directorio padre al path para importar otros módulos
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    sys.path.insert(0, project_root)
    
    try:
        from sincronizador_rss.src.components.config_manager import ConfigManager
        from sincronizador_rss.src.utils.logger import logger
        
        logger.info("--- INICIANDO PRUEBA DE CONEXIÓN A SUPABASE ---")
        
        # 1. Cargar la configuración
        logger.info("Paso 1: Cargando configuración...")
        cfg_manager = ConfigManager()
        supabase_credentials = cfg_manager.get_supabase_credentials()
        logger.info("Credenciales de Supabase cargadas con éxito.")
        
        # 2. Intentar conectar a Supabase
        logger.info("Paso 2: Creando instancia de DatabaseManager para conectar...")
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        # 3. Probar la conexión
        logger.info("Paso 3: Probando la conexión...")
        db_manager.test_connection()
        
        # 4. Cerrar la conexión
        logger.info("Paso 4: Cerrando la conexión...")
        db_manager.close()
        
        logger.info("✅ --- PRUEBA FINALIZADA CON ÉXITO --- ✅")
        return True
        
    except FileNotFoundError as e:
        logger.error(f"❌ ERROR CRÍTICO: No se encontró el archivo de configuración. {e}")
        return False
    except ValueError as e:
        logger.error(f"❌ ERROR CRÍTICO: Faltan variables en el archivo .env. {e}")
        return False
    except Exception as e:
        logger.error(f"❌ ERROR DURANTE LA PRUEBA: {e}")
        return False


if __name__ == "__main__":
    """
    Punto de entrada para ejecutar pruebas directamente desde este archivo.
    Uso: python database_manager.py
    """
    success = test_database_connection()
    exit(0 if success else 1)
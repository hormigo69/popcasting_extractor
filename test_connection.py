# test_connection.py

from sincronizador_rss.src.components.config_manager import ConfigManager
from sincronizador_rss.src.components.database_manager import DatabaseManager
from sincronizador_rss.src.utils.logger import logger # Importamos el logger para ver los mensajes

def test_db_connection():
    """
    Script para probar la conexión a la base de datos.
    """
    logger.info("--- INICIANDO PRUEBA DE CONEXIÓN A SUPABASE ---")
    
    try:
        # 1. Cargar la configuración
        logger.info("Paso 1: Cargando configuración...")
        cfg_manager = ConfigManager()
        supabase_credentials = cfg_manager.get_supabase_credentials()
        logger.info("Credenciales de Supabase cargadas con éxito.")
        # Por seguridad, no imprimimos las credenciales completas
        
        # 2. Intentar conectar a Supabase
        logger.info("Paso 2: Creando instancia de DatabaseManager para conectar...")
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        # Si llegamos aquí, la conexión en el __init__ fue exitosa.
        # db_manager.client contendrá el objeto cliente de Supabase.
        
        # 3. Probar la conexión
        logger.info("Paso 3: Probando la conexión...")
        db_manager.test_connection()
        
        # 4. Cerrar la conexión
        logger.info("Paso 4: Cerrando la conexión...")
        db_manager.close()
        
        logger.info("✅ --- PRUEBA FINALIZADA CON ÉXITO --- ✅")
        
    except FileNotFoundError as e:
        logger.error(f"❌ ERROR CRÍTICO: No se encontró el archivo de configuración. {e}")
    except ValueError as e:
        logger.error(f"❌ ERROR CRÍTICO: Faltan variables en el archivo .env. {e}")
    except Exception as e:
        logger.error(f"❌ ERROR DURANTE LA PRUEBA: {e}")

if __name__ == "__main__":
    test_db_connection() 
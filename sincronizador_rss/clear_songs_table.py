"""
Script para limpiar completamente la tabla songs.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path para importaciones
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

# Importaciones directas sin usar __init__.py
import importlib.util

# Importar DatabaseManager directamente
spec = importlib.util.spec_from_file_location(
    "database_manager", 
    current_dir / "src" / "components" / "database_manager.py"
)
database_manager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database_manager_module)
DatabaseManager = database_manager_module.DatabaseManager

# Importar ConfigManager directamente
spec = importlib.util.spec_from_file_location(
    "config_manager", 
    current_dir / "src" / "components" / "config_manager.py"
)
config_manager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_manager_module)
ConfigManager = config_manager_module.ConfigManager

# Importar logger directamente
spec = importlib.util.spec_from_file_location(
    "logger", 
    current_dir / "src" / "utils" / "logger.py"
)
logger_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logger_module)
logger = logger_module.logger


def clear_songs_table():
    """
    Limpia completamente la tabla songs.
    """
    try:
        logger.info("=== LIMPIANDO TABLA SONGS ===")
        
        # 1. Configurar conexión
        logger.info("1. Configurando conexión...")
        cfg_manager = ConfigManager()
        supabase_credentials = cfg_manager.get_supabase_credentials()
        
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        # 2. Obtener conteo actual
        logger.info("2. Obteniendo conteo actual...")
        result = db_manager.client.table('songs').select('id', count='exact').execute()
        current_count = result.count if hasattr(result, 'count') else 0
        logger.info(f"   Canciones actuales en la tabla: {current_count}")
        
        if current_count == 0:
            logger.info("   ✅ La tabla songs ya está vacía")
            return True
        
        # 3. Confirmar la operación
        logger.warning(f"⚠️  Se van a eliminar {current_count} canciones de la tabla songs")
        confirm = input("¿Estás seguro? (escribe 'SI' para confirmar): ")
        
        if confirm != 'SI':
            logger.info("❌ Operación cancelada por el usuario")
            return False
        
        # 4. Eliminar todas las canciones
        logger.info("3. Eliminando todas las canciones...")
        delete_result = db_manager.client.table('songs').delete().neq('id', 0).execute()
        
        # 5. Verificar que se eliminaron
        logger.info("4. Verificando eliminación...")
        result = db_manager.client.table('songs').select('id', count='exact').execute()
        new_count = result.count if hasattr(result, 'count') else 0
        
        if new_count == 0:
            logger.info("   ✅ Tabla songs limpiada exitosamente")
            logger.info(f"   📊 Canciones eliminadas: {current_count}")
        else:
            logger.error(f"   ❌ Error: quedaron {new_count} canciones")
            return False
        
        # 6. Cerrar conexión
        logger.info("5. Cerrando conexión...")
        db_manager.close()
        
        logger.info("✅ Limpieza completada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error limpiando tabla songs: {e}")
        return False


if __name__ == "__main__":
    success = clear_songs_table()
    if success:
        logger.info("🎉 Tabla songs limpiada correctamente")
    else:
        logger.error("💥 Error al limpiar la tabla songs")
        sys.exit(1) 
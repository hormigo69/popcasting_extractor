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
    
    def get_table_structure_from_sample(self, table_name: str, limit: int = 1):
        """Obtiene la estructura de una tabla analizando una muestra de datos."""
        try:
            # Obtener una muestra de datos
            result = self.client.table(table_name).select("*").limit(limit).execute()
            
            if not result.data:
                self.logger.warning(f"⚠️ Tabla '{table_name}' está vacía")
                return []
            
            # Analizar la estructura del primer registro
            sample_record = result.data[0]
            structure = []
            
            for column_name, value in sample_record.items():
                # Determinar el tipo de dato
                if value is None:
                    data_type = "unknown"
                elif isinstance(value, bool):
                    data_type = "boolean"
                elif isinstance(value, int):
                    data_type = "integer"
                elif isinstance(value, float):
                    data_type = "numeric"
                elif isinstance(value, str):
                    data_type = "text"
                elif isinstance(value, list):
                    data_type = "json"
                elif isinstance(value, dict):
                    data_type = "jsonb"
                else:
                    data_type = str(type(value).__name__)
                
                structure.append({
                    'column_name': column_name,
                    'data_type': data_type,
                    'sample_value': str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                })
            
            self.logger.info(f"✅ Estructura de tabla '{table_name}' obtenida de muestra")
            return structure
            
        except Exception as e:
            self.logger.error(f"❌ Error al obtener estructura de tabla '{table_name}': {e}")
            return []
    
    def get_table_info(self):
        """Obtiene información completa de las tablas conocidas."""
        tables_info = {}
        known_tables = ["podcasts", "songs"]
        
        for table in known_tables:
            structure = self.get_table_structure_from_sample(table)
            tables_info[table] = structure
            self.logger.info(f"📋 Tabla '{table}': {len(structure)} columnas")
        
        return tables_info
    
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
        
        # 4. Obtener información de tablas
        logger.info("Paso 4: Obteniendo información de tablas...")
        tables_info = db_manager.get_table_info()
        
        # 5. Mostrar información
        logger.info("📊 INFORMACIÓN DE TABLAS:")
        for table_name, columns in tables_info.items():
            logger.info(f"\n📋 Tabla: {table_name}")
            for column in columns:
                logger.info(f"  - {column['column_name']}: {column['data_type']} (ejemplo: {column['sample_value']})")
        
        # 6. Cerrar la conexión
        logger.info("Paso 5: Cerrando la conexión...")
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

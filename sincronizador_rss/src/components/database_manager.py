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
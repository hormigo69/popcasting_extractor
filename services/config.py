"""
Configuración para seleccionar entre SQLite y Supabase.
"""

import os

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()

# Validar tipo de base de datos
if DATABASE_TYPE not in ["sqlite", "supabase"]:
    raise ValueError("DATABASE_TYPE debe ser 'sqlite' o 'supabase'")


def get_database_module():
    """
    Retorna el módulo de base de datos apropiado según la configuración.
    """
    if DATABASE_TYPE == "supabase":
        # Importación absoluta para evitar problemas con importaciones relativas
        import services.supabase_database as supabase_database

        return supabase_database
    else:
        # Importación absoluta para evitar problemas con importaciones relativas
        import services.database as database

        return database


def is_supabase_enabled():
    """Verifica si Supabase está habilitado."""
    return DATABASE_TYPE == "supabase"


def is_sqlite_enabled():
    """Verifica si SQLite está habilitado."""
    return DATABASE_TYPE == "sqlite"

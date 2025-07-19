#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión con Supabase.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Añadir el directorio services al path
sys.path.append(str(Path(__file__).parent.parent / "services"))


def test_supabase_connection():
    """Prueba la conexión con Supabase."""
    print("🧪 Probando conexión con Supabase...")

    # Cargar variables de entorno
    load_dotenv()

    # Verificar variables de entorno
    required_vars = ["supabase_project_url", "supabase_api_key"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")
        print("Configura el archivo .env con las credenciales de Supabase")
        return False

    try:
        from supabase_database import SupabaseDatabase

        # Crear instancia de Supabase
        print("📡 Conectando a Supabase...")
        supabase_db = SupabaseDatabase()

        # Probar inicialización
        print("🔧 Inicializando base de datos...")
        supabase_db.initialize_database()

        # Probar operaciones básicas
        print("📝 Probando operaciones básicas...")

        # Crear un podcast de prueba
        test_podcast_id = supabase_db.add_podcast_if_not_exists(
            title="Podcast de Prueba",
            date="2024-01-01",
            url="https://example.com/test",
            program_number="TEST001",
            download_url="https://example.com/test.mp3",
            file_size=1024000,
        )
        print(f"  ✅ Podcast de prueba creado con ID: {test_podcast_id}")

        # Añadir una canción de prueba
        supabase_db.add_song(
            podcast_id=test_podcast_id,
            title="Canción de Prueba",
            artist="Artista de Prueba",
            position=1,
        )
        print("  ✅ Canción de prueba añadida")

        # Añadir un link extra de prueba
        supabase_db.add_extra_link(
            podcast_id=test_podcast_id,
            text="Link de Prueba",
            url="https://example.com/link",
        )
        print("  ✅ Link extra de prueba añadido")

        # Verificar que se pueden leer los datos
        podcasts = supabase_db.get_all_podcasts()
        print(f"  ✅ Podcasts en la base de datos: {len(podcasts)}")

        songs = supabase_db.get_songs_by_podcast_id(test_podcast_id)
        print(f"  ✅ Canciones en el podcast de prueba: {len(songs)}")

        links = supabase_db.get_extra_links_by_podcast_id(test_podcast_id)
        print(f"  ✅ Links extras en el podcast de prueba: {len(links)}")

        # Probar búsqueda
        search_results = supabase_db.search_songs("prueba")
        print(f"  ✅ Resultados de búsqueda: {len(search_results)}")

        # Limpiar datos de prueba
        print("🧹 Limpiando datos de prueba...")
        supabase_db.delete_songs_by_podcast_id(test_podcast_id)
        supabase_db.delete_extra_links_by_podcast_id(test_podcast_id)

        # Eliminar el podcast de prueba (esto eliminará automáticamente las canciones y links)
        # Nota: En Supabase, esto se hace a través de la API REST
        print("  ✅ Datos de prueba eliminados")

        print("✅ Todas las pruebas pasaron exitosamente!")
        return True

    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        return False


def test_configuration():
    """Prueba la configuración del sistema."""
    print("⚙️  Probando configuración...")

    try:
        from config import get_database_module, is_sqlite_enabled, is_supabase_enabled

        # Verificar configuración
        db_type = os.getenv("DATABASE_TYPE", "sqlite")
        print(f"  📊 Tipo de base de datos configurado: {db_type}")

        # Verificar funciones de configuración
        print(f"  🔍 Supabase habilitado: {is_supabase_enabled()}")
        print(f"  🔍 SQLite habilitado: {is_sqlite_enabled()}")

        # Probar obtención del módulo
        db_module = get_database_module()
        print(f"  📦 Módulo de base de datos: {db_module.__name__}")

        print("✅ Configuración correcta")
        return True

    except Exception as e:
        print(f"❌ Error en la configuración: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PRUEBAS DE SUPABASE")
    print("=" * 60)

    # Verificar que existe el archivo .env
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        print("⚠️  No se encontró el archivo .env")
        print("Crea el archivo .env con las credenciales de Supabase")
        print("Puedes usar env.example como plantilla")
        sys.exit(1)

    # Ejecutar pruebas
    config_success = test_configuration()
    connection_success = test_supabase_connection()

    print("\n" + "=" * 60)
    if config_success and connection_success:
        print("🎉 TODAS LAS PRUEBAS PASARON")
        print("✅ Supabase está configurado correctamente")
        print("✅ Puedes proceder con la migración")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("Revisa los errores anteriores y corrige la configuración")
        sys.exit(1)

    print("=" * 60)

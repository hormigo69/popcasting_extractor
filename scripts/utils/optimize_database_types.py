#!/usr/bin/env python3
"""
Script para optimizar los tipos de campo de la base de datos.
Convierte los campos de TEXT a tipos más específicos según las especificaciones.

Campos a optimizar en la tabla podcasts:
- program_number: TEXT -> INTEGER
- date: TEXT -> DATE
- title: TEXT (mantener)
- url: TEXT (mantener)
- download_url: TEXT (mantener)
- cover_image_url: TEXT (mantener)
"""

import os
import re
import sys
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.config import DATABASE_TYPE
from services.database import get_db_connection
from services.supabase_database import SupabaseDatabase


def validate_program_number(program_number: str) -> int | None:
    """
    Valida y convierte program_number a entero.
    Retorna None si no es válido.
    """
    if not program_number:
        return None

    try:
        # Limpiar el string de caracteres no numéricos
        cleaned = re.sub(r"[^\d]", "", str(program_number))
        if cleaned:
            return int(cleaned)
        return None
    except (ValueError, TypeError):
        return None


def validate_date(date_str: str) -> str | None:
    """
    Valida y normaliza la fecha al formato YYYY-MM-DD.
    Retorna None si no es válida.
    """
    if not date_str:
        return None

    # Intentar diferentes formatos de fecha
    date_formats = [
        "%Y-%m-%d",  # 2023-12-25
        "%d/%m/%Y",  # 25/12/2023
        "%d.%m.%Y",  # 25.12.2023
        "%Y/%m/%d",  # 2023/12/25
        "%d-%m-%Y",  # 25-12-2023
        "%Y-%m-%d %H:%M:%S",  # 2023-12-25 14:30:00
        "%a, %d %b %Y %H:%M:%S %z",  # Mon, 25 Dec 2023 14:30:00 +0000
    ]

    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def optimize_sqlite_database():
    """
    Optimiza los tipos de campo en la base de datos SQLite.
    """
    print("🔄 Optimizando tipos de campo en SQLite...")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Obtener todos los podcasts
        cursor.execute("SELECT id, program_number, date FROM podcasts")
        podcasts = cursor.fetchall()

        print(f"📊 Procesando {len(podcasts)} episodios...")

        updated_program_numbers = 0
        updated_dates = 0
        errors = 0

        for podcast in podcasts:
            podcast_id, program_number, date = podcast

            try:
                # Validar y convertir program_number
                valid_program_number = validate_program_number(program_number)
                if valid_program_number is not None and str(
                    valid_program_number
                ) != str(program_number):
                    cursor.execute(
                        "UPDATE podcasts SET program_number = ? WHERE id = ?",
                        (valid_program_number, podcast_id),
                    )
                    updated_program_numbers += 1
                    print(
                        f"  ✅ Episodio {podcast_id}: program_number '{program_number}' -> {valid_program_number}"
                    )

                # Validar y convertir date
                valid_date = validate_date(date)
                if valid_date is not None and valid_date != date:
                    cursor.execute(
                        "UPDATE podcasts SET date = ? WHERE id = ?",
                        (valid_date, podcast_id),
                    )
                    updated_dates += 1
                    print(f"  ✅ Episodio {podcast_id}: date '{date}' -> {valid_date}")

            except Exception as e:
                print(f"  ❌ Error procesando episodio {podcast_id}: {e}")
                errors += 1

        # Crear nueva tabla con tipos optimizados
        print("\n🔄 Creando nueva tabla con tipos optimizados...")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS podcasts_optimized (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date DATE NOT NULL UNIQUE,
                url TEXT,
                download_url TEXT,
                file_size INTEGER,
                program_number INTEGER,
                wordpress_url TEXT,
                cover_image_url TEXT,
                web_extra_links TEXT,
                web_playlist TEXT,
                last_web_check TEXT
            )
        """)

        # Copiar datos a la nueva tabla
        cursor.execute("""
            INSERT INTO podcasts_optimized
            SELECT id, title, date, url, download_url, file_size,
                   CAST(program_number AS INTEGER), wordpress_url,
                   cover_image_url, web_extra_links, web_playlist, last_web_check
            FROM podcasts
        """)

        # Renombrar tablas
        cursor.execute("DROP TABLE podcasts")
        cursor.execute("ALTER TABLE podcasts_optimized RENAME TO podcasts")

        # Recrear índices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_podcasts_date ON podcasts(date)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_podcasts_program_number ON podcasts(program_number)"
        )

        conn.commit()

        print("\n📊 Resumen de optimización SQLite:")
        print(f"  - Program numbers actualizados: {updated_program_numbers}")
        print(f"  - Fechas actualizadas: {updated_dates}")
        print(f"  - Errores: {errors}")
        print("  - Tabla recreada con tipos optimizados")

    except Exception as e:
        print(f"❌ Error durante la optimización SQLite: {e}")
        conn.rollback()
    finally:
        conn.close()


def optimize_supabase_database():
    """
    Optimiza los tipos de campo en la base de datos Supabase.
    """
    print("🔄 Optimizando tipos de campo en Supabase...")

    db = SupabaseDatabase()

    try:
        # Obtener todos los podcasts
        podcasts = db.get_all_podcasts()

        print(f"📊 Procesando {len(podcasts)} episodios...")

        updated_program_numbers = 0
        updated_dates = 0
        errors = 0

        for podcast in podcasts:
            podcast_id = podcast["id"]
            program_number = podcast.get("program_number")
            date = podcast.get("date")

            try:
                update_data = {}

                # Validar y convertir program_number
                valid_program_number = validate_program_number(program_number)
                if valid_program_number is not None and str(
                    valid_program_number
                ) != str(program_number):
                    update_data["program_number"] = valid_program_number
                    updated_program_numbers += 1
                    print(
                        f"  ✅ Episodio {podcast_id}: program_number '{program_number}' -> {valid_program_number}"
                    )

                # Validar y convertir date
                valid_date = validate_date(date)
                if valid_date is not None and valid_date != date:
                    update_data["date"] = valid_date
                    updated_dates += 1
                    print(f"  ✅ Episodio {podcast_id}: date '{date}' -> {valid_date}")

                # Actualizar si hay cambios
                if update_data:
                    db.client.table("podcasts").update(update_data).eq(
                        "id", podcast_id
                    ).execute()

            except Exception as e:
                print(f"  ❌ Error procesando episodio {podcast_id}: {e}")
                errors += 1

        print("\n📊 Resumen de optimización Supabase:")
        print(f"  - Program numbers actualizados: {updated_program_numbers}")
        print(f"  - Fechas actualizadas: {updated_dates}")
        print(f"  - Errores: {errors}")

        # Nota: Para cambiar tipos de columna en Supabase, se necesita ejecutar SQL manualmente
        print(
            "\n⚠️  Nota: Para cambiar tipos de columna en Supabase, ejecuta manualmente:"
        )
        print("""
        -- En el SQL Editor de Supabase:
        ALTER TABLE podcasts
        ALTER COLUMN program_number TYPE INTEGER USING program_number::INTEGER,
        ALTER COLUMN date TYPE DATE USING date::DATE;
        """)

    except Exception as e:
        print(f"❌ Error durante la optimización Supabase: {e}")


def main():
    """
    Función principal que determina qué base de datos optimizar.
    """
    print("🔧 OPTIMIZADOR DE TIPOS DE BASE DE DATOS")
    print("=" * 50)

    print(f"📊 Tipo de base de datos detectado: {DATABASE_TYPE}")

    if DATABASE_TYPE == "sqlite":
        optimize_sqlite_database()
    elif DATABASE_TYPE == "supabase":
        optimize_supabase_database()
    else:
        print(f"❌ Tipo de base de datos no soportado: {DATABASE_TYPE}")
        return

    print("\n✅ Optimización completada!")


if __name__ == "__main__":
    main()

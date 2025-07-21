#!/usr/bin/env python3
"""
Script para eliminar episodios con fechas en formato DD.MM.YYYY.
Estos episodios ya tienen versiones correctas con fechas normalizadas.
"""

import os
import re
import sys
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.supabase_database import SupabaseDatabase


def parse_date_dd_mm_yyyy(date_str):
    """
    Parsea una fecha en formato DD.MM.YYYY y la convierte a YYYY-MM-DD.
    """
    if not date_str or "." not in str(date_str):
        return None

    pattern = r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$"
    match = re.match(pattern, str(date_str))

    if not match:
        return None

    day, month, year = match.groups()
    try:
        dt = datetime(int(year), int(month), int(day))
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None


def clean_duplicate_episodes():
    """
    Elimina episodios con fechas en formato DD.MM.YYYY que ya tienen versiones correctas.
    """
    print("🧹 LIMPIANDO EPISODIOS DUPLICADOS")
    print("=" * 60)

    db = SupabaseDatabase()

    try:
        # Obtener todos los podcasts
        podcasts = db.get_all_podcasts()

        print(f"📊 Total de episodios: {len(podcasts)}")

        # Encontrar episodios con fechas en formato DD.MM.YYYY
        episodes_to_delete = []

        for podcast in podcasts:
            date = podcast.get("date")
            if date and "." in str(date):
                normalized_date = parse_date_dd_mm_yyyy(date)
                if normalized_date:
                    # Verificar si ya existe un episodio con la fecha normalizada
                    for other_podcast in podcasts:
                        if (
                            other_podcast["id"] != podcast["id"]
                            and other_podcast.get("date") == normalized_date
                        ):
                            episodes_to_delete.append(
                                {
                                    "id": podcast["id"],
                                    "program_number": podcast.get("program_number"),
                                    "old_date": date,
                                    "normalized_date": normalized_date,
                                    "duplicate_id": other_podcast["id"],
                                    "duplicate_program_number": other_podcast.get(
                                        "program_number"
                                    ),
                                    "title": podcast.get("title", "Sin título"),
                                }
                            )
                            break

        print(f"📅 Episodios a eliminar: {len(episodes_to_delete)}")

        if not episodes_to_delete:
            print("✅ No se encontraron episodios duplicados para eliminar.")
            return

        # Mostrar los episodios que se van a eliminar
        print("\n📋 Episodios a eliminar:")
        for episode in episodes_to_delete:
            print(f"\n  Episodio #{episode['program_number']} (ID {episode['id']}):")
            print(f"    Fecha actual: {episode['old_date']}")
            print(f"    Fecha normalizada: {episode['normalized_date']}")
            print(
                f"    Duplicado con: Episodio #{episode['duplicate_program_number']} (ID {episode['duplicate_id']})"
            )
            print(f"    Título: {episode['title'][:50]}...")

        # Confirmar con el usuario
        print(f"\n⚠️  Se van a eliminar {len(episodes_to_delete)} episodios duplicados.")
        print(
            "   Estos episodios ya tienen versiones correctas con fechas normalizadas."
        )

        response = input("\n¿Continuar con la eliminación? (s/N): ").strip().lower()
        if response not in ["s", "si", "sí", "y", "yes"]:
            print("❌ Eliminación cancelada por el usuario.")
            return

        # Eliminar los episodios
        print("\n🔄 Eliminando episodios duplicados...")
        deleted_count = 0
        errors = 0

        for episode in episodes_to_delete:
            try:
                # Eliminar el episodio de Supabase
                db.client.table("podcasts").delete().eq("id", episode["id"]).execute()

                deleted_count += 1
                print(
                    f"  ✅ Eliminado ID {episode['id']}: #{episode['program_number']} - {episode['old_date']}"
                )

            except Exception as e:
                errors += 1
                print(f"  ❌ Error eliminando ID {episode['id']}: {e}")

        print("\n📊 Resumen de eliminación:")
        print(f"  - Episodios eliminados: {deleted_count}")
        print(f"  - Errores: {errors}")

        if deleted_count > 0:
            print("\n✅ Limpieza completada exitosamente!")
            print("   Ahora es seguro cambiar los tipos de columna.")

    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        raise


def main():
    """Función principal."""
    clean_duplicate_episodes()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
import re
import sys
from services.supabase_database import SupabaseDatabase

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

Script para normalizar las fechas problemáticas en Supabase.
Convierte fechas en formato DD.MM.YYYY a YYYY-MM-DD antes de cambiar tipos.
"""


# Agregar el directorio raíz al path


def normalize_date_format(date_str):
    """
    Normaliza una fecha del formato DD.MM.YYYY a YYYY-MM-DD.
    """
    if not date_str:
        return None

    # Patrón para DD.MM.YYYY
    pattern = r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$"
    match = re.match(pattern, str(date_str))

    if match:
        day, month, year = match.groups()
        try:
            # Crear fecha y validar
            dt = datetime(int(year), int(month), int(day))
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    return None


def normalize_supabase_dates():
    """
    Normaliza las fechas problemáticas en Supabase.
    """
    print("🔄 NORMALIZANDO FECHAS EN SUPABASE")
    print("=" * 60)

    db = SupabaseDatabase()

    try:
        # Obtener todos los podcasts
        podcasts = db.get_all_podcasts()

        print(f"📊 Total de episodios: {len(podcasts)}")

        # Encontrar fechas que necesitan normalización
        dates_to_normalize = []

        for podcast in podcasts:
            date = podcast.get("date")
            if date:
                normalized = normalize_date_format(date)
                if normalized and normalized != str(date):
                    dates_to_normalize.append(
                        {
                            "id": podcast["id"],
                            "old_date": date,
                            "new_date": normalized,
                            "title": podcast.get("title", "Sin título"),
                        }
                    )

        print(f"📅 Fechas que necesitan normalización: {len(dates_to_normalize)}")

        if not dates_to_normalize:
            print("✅ Todas las fechas ya están en formato correcto.")
            return

        # Mostrar las fechas que se van a normalizar
        print("\n📋 Fechas a normalizar:")
        for item in dates_to_normalize:
            print(
                f"  - ID {item['id']}: '{item['old_date']}' → '{item['new_date']}' ({item['title'][:50]}...)"
            )

        # Confirmar con el usuario
        print(f"\n⚠️  Se van a normalizar {len(dates_to_normalize)} fechas.")
        response = input("¿Continuar? (s/N): ").strip().lower()
        if response not in ["s", "si", "sí", "y", "yes"]:
            print("❌ Normalización cancelada por el usuario.")
            return

        # Normalizar las fechas
        print("\n🔄 Normalizando fechas...")
        updated_count = 0
        errors = 0

        for item in dates_to_normalize:
            try:
                # Actualizar la fecha en Supabase
                db.client.table("podcasts").update({"date": item["new_date"]}).eq(
                    "id", item["id"]
                ).execute()

                updated_count += 1
                print(
                    f"  ✅ ID {item['id']}: '{item['old_date']}' → '{item['new_date']}'"
                )

            except Exception as e:
                errors += 1
                print(f"  ❌ Error actualizando ID {item['id']}: {e}")

        print("\n📊 Resumen de normalización:")
        print(f"  - Fechas actualizadas: {updated_count}")
        print(f"  - Errores: {errors}")

        if updated_count > 0:
            print("\n✅ Normalización completada exitosamente!")
            print("   Ahora es seguro cambiar los tipos de columna.")

    except Exception as e:
        print(f"❌ Error durante la normalización: {e}")
        raise


def main():
    """Función principal."""
    normalize_supabase_dates()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script para corregir la coherencia de URLs - Paso 2.
Limpia duplicados eliminando URLs de wordpress_url en episodios 0-91.
"""

import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.supabase_database import SupabaseDatabase


def fix_url_coherence_step2():
    """Corrige la coherencia de URLs - Paso 2: Limpiar duplicados."""

    print("🔧 CORRECCIÓN DE COHERENCIA DE URLs - PASO 2")
    print("=" * 50)

    # Conectar a Supabase
    db = SupabaseDatabase()

    # Obtener episodios 0-91 con URLs duplicadas
    response = (
        db.client.table("podcasts")
        .select("program_number,title,url,wordpress_url")
        .lte("program_number", 91)
        .execute()
    )

    episodes = response.data

    # Filtrar episodios con URLs duplicadas (misma URL en ambos campos)
    duplicates_to_clean = []

    for ep in episodes:
        if ep["url"] and ep["wordpress_url"] and ep["url"] == ep["wordpress_url"]:
            duplicates_to_clean.append(ep)

    print(
        f"📊 Episodios 0-91 con URLs duplicadas encontrados: {len(duplicates_to_clean)}"
    )
    print()

    if not duplicates_to_clean:
        print("✅ No hay duplicados que limpiar")
        return

    print("🧹 LIMPIANDO DUPLICADOS:")
    print("-" * 30)

    cleaned_count = 0

    for ep in duplicates_to_clean:
        print(f"Episodio #{ep['program_number']}: {ep['title']}")
        print(f"  URL duplicada: {ep['url']}")

        # Limpiar wordpress_url (dejar vacío)
        response = (
            db.client.table("podcasts")
            .update({"wordpress_url": None})
            .eq("program_number", ep["program_number"])
            .execute()
        )

        if response.data:
            print("  ✅ Limpiado correctamente")
            cleaned_count += 1
        else:
            print("  ❌ Error al limpiar")

    print()
    print("✅ Limpieza completada")
    print()
    print("📊 RESUMEN:")
    print(f"   - {cleaned_count} episodios limpiados")
    print(f"   - {len(duplicates_to_clean) - cleaned_count} errores")


if __name__ == "__main__":
    fix_url_coherence_step2()

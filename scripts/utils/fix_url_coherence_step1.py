#!/usr/bin/env python3
"""
Script para corregir la coherencia de URLs - Paso 1.
Corrige episodios que necesitan URLs de iVoox o deja vacío el campo url.
"""

import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.supabase_database import SupabaseDatabase


def fix_url_coherence_step1():
    """Corrige la coherencia de URLs - Paso 1."""

    print("🔧 CORRECCIÓN DE COHERENCIA DE URLs - PASO 1")
    print("=" * 50)

    # Conectar a Supabase
    db = SupabaseDatabase()

    # Definir las correcciones
    corrections = {
        92: "https://www.ivoox.com/en/popcasting92-audios-mp3_rf_58471_1.html",
        93: "https://www.ivoox.com/en/popcasting93-audios-mp3_rf_61158_1.html",
    }

    # Episodios que deben quedar con URL vacía
    episodes_to_empty = [97, 99, 100, 102, 103, 104, 105, 106, 148]

    print("📋 CORRECCIONES A APLICAR:")
    print("-" * 30)

    # Aplicar correcciones con URLs de iVoox
    print("1. Episodios que reciben URL de iVoox:")
    for episode_num, ivoox_url in corrections.items():
        print(f"   Episodio #{episode_num}: {ivoox_url}")

        # Actualizar en la base de datos
        response = (
            db.client.table("podcasts")
            .update({"url": ivoox_url})
            .eq("program_number", episode_num)
            .execute()
        )

        if response.data:
            print(f"   ✅ Episodio #{episode_num} actualizado correctamente")
        else:
            print(f"   ❌ Error al actualizar episodio #{episode_num}")

    print()

    # Aplicar correcciones con URL vacía
    print("2. Episodios que quedan con URL vacía:")
    for episode_num in episodes_to_empty:
        print(f"   Episodio #{episode_num}")

        # Actualizar en la base de datos
        response = (
            db.client.table("podcasts")
            .update({"url": None})
            .eq("program_number", episode_num)
            .execute()
        )

        if response.data:
            print(f"   ✅ Episodio #{episode_num} actualizado correctamente")
        else:
            print(f"   ❌ Error al actualizar episodio #{episode_num}")

    print()
    print("✅ Correcciones aplicadas correctamente")
    print()
    print("📊 RESUMEN:")
    print(f"   - {len(corrections)} episodios con URL de iVoox añadida")
    print(f"   - {len(episodes_to_empty)} episodios con URL vaciada")


if __name__ == "__main__":
    fix_url_coherence_step1()

#!/usr/bin/env python3
"""
Script para listar los episodios que necesitan URLs de iVoox.
"""

import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.supabase_database import SupabaseDatabase


def list_episodes_needing_ivoox_urls():
    """Lista los episodios que necesitan URLs de iVoox."""

    print("🔍 EPISODIOS QUE NECESITAN URLs DE IVOOX")
    print("=" * 50)

    # Conectar a Supabase
    db = SupabaseDatabase()

    # Obtener episodios con WordPress en el campo url
    response = (
        db.client.table("podcasts")
        .select("program_number,title,url,wordpress_url,date")
        .order("program_number")
        .execute()
    )

    episodes = response.data

    # Filtrar episodios que tienen WordPress en url (episodios 92+)
    episodes_needing_ivoox = []

    for ep in episodes:
        if (
            ep["program_number"] >= 92
            and ep["url"]
            and "popcastingpop.com" in ep["url"]
        ):
            episodes_needing_ivoox.append(ep)

    print(
        f"📊 Total de episodios que necesitan URLs de iVoox: {len(episodes_needing_ivoox)}"
    )
    print()

    print("📋 LISTA DE EPISODIOS:")
    print("-" * 30)

    for ep in episodes_needing_ivoox:
        print(f"Episodio #{ep['program_number']}: {ep['title']}")
        print(f"  Fecha: {ep['date']}")
        print(f"  URL actual (WordPress): {ep['url']}")
        print(f"  WordPress URL: {ep['wordpress_url']}")
        print()

    print("🔧 ACCIÓN REQUERIDA:")
    print("Necesitas buscar las URLs de iVoox para estos episodios y proporcionarlas.")
    print("Las URLs de iVoox deberían tener el formato:")
    print("https://www.ivoox.com/popcasting[numero]-audios-mp3_rf_[id]_1.html")


if __name__ == "__main__":
    list_episodes_needing_ivoox_urls()

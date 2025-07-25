#!/usr/bin/env python3
"""
Script temporal para eliminar comentarios que empiecen por "Especial verano".
"""

import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# Añadir el directorio raíz al path para importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.config import get_database_module


def clean_summer_comments():
    """
    Elimina todos los comentarios que empiecen por "Especial verano".
    """
    db = get_database_module()

    print("🧹 Limpiando comentarios de especiales de verano...")
    print("=" * 50)

    # Obtener todos los episodios
    podcasts = db.get_all_podcasts()

    cleaned_count = 0

    for podcast in podcasts:
        web_info = db.get_podcast_web_info(podcast["id"])
        current_comments = web_info.get("comments") if web_info else None

        if current_comments and current_comments.startswith("Especial verano"):
            # Eliminar el comentario
            db.update_web_info(podcast_id=podcast["id"], comments=None)
            print(
                f"🗑️  Eliminado comentario en episodio #{podcast['program_number']}: {current_comments}"
            )
            cleaned_count += 1

    print("\n📊 Resumen:")
    print(f"   Comentarios eliminados: {cleaned_count}")
    print(f"   Total episodios procesados: {len(podcasts)}")


def main():
    """
    Función principal.
    """
    print("🧹 Limpiar Comentarios de Especiales de Verano")
    print("=" * 50)

    try:
        clean_summer_comments()
        print("\n🎉 Limpieza completada!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

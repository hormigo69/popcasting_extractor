#!/usr/bin/env python3
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
from config import DATABASE_TYPE
from database import get_db_connection, initialize_database
from supabase_database import get_supabase_connection

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

Script para analizar la distribución de canciones por episodio en toda la base de datos.
"""

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))


def get_database_wrapper():
    """
    Obtiene la instancia de base de datos correcta según la configuración.
    """
    if DATABASE_TYPE == "supabase":
        return get_supabase_connection()
    else:
        initialize_database()

        # Crear un wrapper para mantener compatibilidad con la interfaz
        class DatabaseWrapper:
            def __init__(self, conn):
                self.conn = conn
                self.cursor = conn.cursor()

            def get_all_podcasts_with_songs_count(self):
                self.cursor.execute("""
                    SELECT program_number, title, date, web_songs_count
                    FROM podcasts
                    WHERE web_songs_count IS NOT NULL
                    ORDER BY web_songs_count DESC, program_number
                """)
                return [dict(row) for row in self.cursor.fetchall()]

            def get_songs_count_distribution(self):
                self.cursor.execute("""
                    SELECT web_songs_count, COUNT(*) as count
                    FROM podcasts
                    WHERE web_songs_count IS NOT NULL
                    GROUP BY web_songs_count
                    ORDER BY web_songs_count
                """)
                return [dict(row) for row in self.cursor.fetchall()]

        return DatabaseWrapper(get_db_connection())


def analyze_songs_distribution():
    """
    Analiza la distribución de canciones por episodio.
    """
    try:
        db = get_database_wrapper()
        print("✅ Conexión a la base de datos establecida")

        # Obtener distribución de canciones
        if DATABASE_TYPE == "supabase":
            response = (
                db.client.table("podcasts")
                .select("web_songs_count")
                .not_.is_("web_songs_count", "null")
                .execute()
            )

            # Contar episodios por número de canciones
            distribution = {}
            for episode in response.data:
                count = episode["web_songs_count"]
                distribution[count] = distribution.get(count, 0) + 1

            # Convertir a lista ordenada
            distribution_list = [
                {"web_songs_count": k, "count": v} for k, v in distribution.items()
            ]
            distribution_list.sort(key=lambda x: x["web_songs_count"])

            # Obtener todos los episodios con su número de canciones
            all_episodes_response = (
                db.client.table("podcasts")
                .select("program_number, title, date, web_songs_count")
                .not_.is_("web_songs_count", "null")
                .order("web_songs_count", desc=True)
                .execute()
            )

            all_episodes = all_episodes_response.data

        else:
            distribution_list = db.get_songs_count_distribution()
            all_episodes = db.get_all_podcasts_with_songs_count()

        # Mostrar estadísticas generales
        total_episodes = len(all_episodes)
        total_songs = sum(ep["web_songs_count"] for ep in all_episodes)
        avg_songs = total_songs / total_episodes if total_episodes > 0 else 0

        print("\n📊 ESTADÍSTICAS GENERALES")
        print("=" * 50)
        print(f"Total de episodios con playlist: {total_episodes}")
        print(f"Total de canciones: {total_songs}")
        print(f"Promedio de canciones por episodio: {avg_songs:.1f}")

        # Mostrar distribución
        print("\n📈 DISTRIBUCIÓN DE CANCIONES POR EPISODIO")
        print("=" * 50)
        print(f"{'Canciones':<10} {'Episodios':<10} {'Porcentaje':<12} {'Barra':<20}")
        print("-" * 50)

        for item in distribution_list:
            songs = item["web_songs_count"]
            count = item["count"]
            percentage = (count / total_episodes) * 100
            bar = "█" * int(percentage / 2)  # Barra visual
            print(f"{songs:<10} {count:<10} {percentage:>6.1f}%     {bar}")

        # Mostrar episodios con más y menos canciones
        if all_episodes:
            print("\n🏆 EPISODIOS CON MÁS CANCIONES")
            print("-" * 40)
            for i, ep in enumerate(all_episodes[:10]):
                print(
                    f"{i+1:2d}. #{ep['program_number']:>3} | {ep['web_songs_count']:>2} canciones | {ep['date']} | {ep['title'][:40]}..."
                )

            print("\n📉 EPISODIOS CON MENOS CANCIONES")
            print("-" * 40)
            for i, ep in enumerate(all_episodes[-10:]):
                print(
                    f"{i+1:2d}. #{ep['program_number']:>3} | {ep['web_songs_count']:>2} canciones | {ep['date']} | {ep['title'][:40]}..."
                )

        # Estadísticas adicionales
        if all_episodes:
            songs_counts = [ep["web_songs_count"] for ep in all_episodes]
            min_songs = min(songs_counts)
            max_songs = max(songs_counts)
            median_songs = sorted(songs_counts)[len(songs_counts) // 2]

            print("\n📋 ESTADÍSTICAS ADICIONALES")
            print("-" * 30)
            print(f"Mínimo de canciones: {min_songs}")
            print(f"Máximo de canciones: {max_songs}")
            print(f"Mediana de canciones: {median_songs}")

            # Rango más común
            most_common = max(distribution_list, key=lambda x: x["count"])
            print(
                f"Rango más común: {most_common['web_songs_count']} canciones ({most_common['count']} episodios)"
            )

        return distribution_list, all_episodes

    except Exception as e:
        print(f"❌ Error: {e}")
        return [], []


def main():
    """Función principal del script."""
    print("🎵 Analizador de distribución de canciones por episodio")
    print("=" * 60)

    distribution, episodes = analyze_songs_distribution()

    print("\n✅ Análisis completado")
    print(f"📊 Se analizaron {len(episodes)} episodios con playlist")


if __name__ == "__main__":
    main()

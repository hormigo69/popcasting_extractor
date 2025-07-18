#!/usr/bin/env python3
"""
Análisis simple de logs de extracción
"""

import re


def analyze_logs():
    """Analiza los logs de forma simple"""
    print("📋 ANÁLISIS SIMPLE DE LOGS")
    print("=" * 50)

    # Analizar errores de parsing
    print("🔍 ERRORES DE PARSING:")
    print("-" * 30)

    with open("logs/parsing_errors.log", encoding="utf-8") as f:
        content = f.read()

    # Contar errores por tipo
    error_counts = {
        "Entrada inválida descartada": len(
            re.findall(r"Entrada inválida descartada", content)
        ),
        "Entrada sin separador descartada": len(
            re.findall(r"Entrada sin separador descartada", content)
        ),
        "No se pudo parsear": len(re.findall(r"No se pudo parsear", content)),
        "Entrada inválida (post-limpieza)": len(
            re.findall(r"Entrada inválida \(post-limpieza\)", content)
        ),
    }

    total_errors = sum(error_counts.values())
    print(f"📊 Total de errores: {total_errors}")
    print()

    for error_type, count in error_counts.items():
        if count > 0:
            percentage = (count / total_errors) * 100
            print(f"   {error_type}: {count} ({percentage:.1f}%)")
    print()

    # Analizar estadísticas de extracción
    print("📈 ESTADÍSTICAS DE EXTRACCIÓN:")
    print("-" * 30)

    with open("logs/extraction_stats.log", encoding="utf-8") as f:
        content = f.read()

    # Extraer estadísticas
    episodes_match = re.search(r"Total de episodios procesados: (\d+)", content)
    songs_match = re.search(r"Total de canciones añadidas/actualizadas: (\d+)", content)

    if episodes_match and songs_match:
        episodes = int(episodes_match.group(1))
        songs = int(songs_match.group(1))

        print(f"📊 Episodios procesados: {episodes}")
        print(f"🎵 Canciones extraídas: {songs}")
        print(f"📈 Promedio de canciones por episodio: {songs/episodes:.1f}")
    else:
        print("❌ No se encontraron estadísticas")
    print()

    # Resumen de mejoras
    print("🎯 RESUMEN DE MEJORAS:")
    print("-" * 30)

    new_parser_errors = (
        error_counts["Entrada inválida descartada"]
        + error_counts["Entrada sin separador descartada"]
    )
    old_parser_errors = (
        error_counts["No se pudo parsear"]
        + error_counts["Entrada inválida (post-limpieza)"]
    )

    print(f"✅ Errores del nuevo parser: {new_parser_errors}")
    print(f"❌ Errores del parser anterior: {old_parser_errors}")

    if old_parser_errors > 0:
        improvement = (
            (old_parser_errors - new_parser_errors) / old_parser_errors
        ) * 100
        print(f"📈 Mejora: {improvement:.1f}% menos errores")

    print()
    print("🎉 Análisis completado!")


if __name__ == "__main__":
    analyze_logs()

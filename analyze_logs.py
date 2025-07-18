#!/usr/bin/env python3
"""
Script para analizar los logs de extracción y generar reportes
"""

import os
import re
from datetime import datetime
from collections import defaultdict, Counter

def analyze_parsing_errors():
    """Analiza los errores de parsing del archivo de log"""
    log_file = "logs/parsing_errors.log"
    
    if not os.path.exists(log_file):
        print("❌ No se encontró el archivo de errores de parsing")
        return
    
    print("🔍 ANALIZANDO ERRORES DE PARSING")
    print("=" * 50)
    
    errors_by_podcast = defaultdict(list)
    error_types = Counter()
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # Dividir por líneas que empiecen con timestamp
        lines = re.split(r'\n(?=\d{4}-\d{2}-\d{2})', content)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Extraer información del log
            match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - WARNING - Podcast: (.+?) - (.+)', line)
            if match:
                timestamp, podcast, error_msg = match.groups()
                errors_by_podcast[podcast].append({
                    'timestamp': timestamp,
                    'error': error_msg
                })
                
                # Categorizar tipos de error
                if 'Entrada inválida descartada' in error_msg:
                    error_types['Entrada inválida'] += 1
                elif 'Entrada sin separador descartada' in error_msg:
                    error_types['Sin separador'] += 1
                elif 'No se pudo parsear' in error_msg:
                    error_types['Parser anterior'] += 1
                else:
                    error_types['Otros'] += 1
    
    # Estadísticas generales
    total_errors = sum(len(errors) for errors in errors_by_podcast.values())
    total_podcasts_with_errors = len(errors_by_podcast)
    
    print("📊 Estadísticas generales:")
    print(f"   Total de errores: {total_errors}")
    print(f"   Podcasts con errores: {total_podcasts_with_errors}")
    print()
    
    # Tipos de errores
    print("📋 Tipos de errores:")
    for error_type, count in error_types.most_common():
        percentage = (count / total_errors) * 100 if total_errors > 0 else 0
        print(f"   {error_type}: {count} ({percentage:.1f}%)")
    print()
    
    # Podcasts con más errores
    print("🎯 Podcasts con más errores:")
    sorted_podcasts = sorted(errors_by_podcast.items(), key=lambda x: len(x[1]), reverse=True)
    for podcast, errors in sorted_podcasts[:10]:
        print(f"   {podcast}: {len(errors)} errores")
    print()
    
    # Ejemplos de errores
    print("💡 Ejemplos de errores:")
    for podcast, errors in sorted_podcasts[:3]:
        print(f"   {podcast}:")
        for error in errors[:2]:  # Mostrar solo los primeros 2 errores
            print(f"     - {error['error']}")
        print()

def analyze_extraction_stats():
    """Analiza las estadísticas de extracción del archivo de log"""
    log_file = "logs/extraction_stats.log"
    
    if not os.path.exists(log_file):
        print("❌ No se encontró el archivo de estadísticas de extracción")
        return
    
    print("📈 ANALIZANDO ESTADÍSTICAS DE EXTRACCIÓN")
    print("=" * 50)
    
    extractions = []
    current_extraction = {}
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # Dividir por líneas que empiecen con timestamp
        lines = re.split(r'\n(?=\d{4}-\d{2}-\d{2})', content)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Extraer información del log
            match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (.+)', line)
            if match:
                timestamp, level, message = match.groups()
                
                if 'Proceso de extracción finalizado' in message:
                    if current_extraction:
                        extractions.append(current_extraction)
                    current_extraction = {'timestamp': timestamp}
                elif 'Total de episodios procesados' in message:
                    match = re.search(r'(\d+)', message)
                    if match:
                        current_extraction['episodes'] = int(match.group(1))
                elif 'Total de canciones añadidas/actualizadas' in message:
                    match = re.search(r'(\d+)', message)
                    if match:
                        current_extraction['songs'] = int(match.group(1))
    
    # Añadir la última extracción si existe
    if current_extraction:
        extractions.append(current_extraction)
    
    if not extractions:
        print("❌ No se encontraron datos de extracción")
        return
    
    print(f"📊 Total de extracciones registradas: {len(extractions)}")
    print()
    
    # Estadísticas de la última extracción
    latest = extractions[-1]
    print("🔄 Última extracción:")
    print(f"   Fecha: {latest['timestamp']}")
    print(f"   Episodios: {latest.get('episodes', 'N/A')}")
    print(f"   Canciones: {latest.get('songs', 'N/A')}")
    print()
    
    # Estadísticas históricas
    if len(extractions) > 1:
        print("📈 Estadísticas históricas:")
        episodes_list = [e.get('episodes', 0) for e in extractions if 'episodes' in e]
        songs_list = [e.get('songs', 0) for e in extractions if 'songs' in e]
        
        if episodes_list:
            print(f"   Promedio de episodios por extracción: {sum(episodes_list) / len(episodes_list):.1f}")
            print(f"   Máximo episodios en una extracción: {max(episodes_list)}")
            print(f"   Mínimo episodios en una extracción: {min(episodes_list)}")
        
        if songs_list:
            print(f"   Promedio de canciones por extracción: {sum(songs_list) / len(songs_list):.1f}")
            print(f"   Máximo canciones en una extracción: {max(songs_list)}")
            print(f"   Mínimo canciones en una extracción: {min(songs_list)}")
        print()

def generate_summary_report():
    """Genera un reporte resumido de todos los logs"""
    print("📋 REPORTE RESUMIDO DE LOGS")
    print("=" * 50)
    print(f"📅 Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar archivos de log
    parsing_log = "logs/parsing_errors.log"
    stats_log = "logs/extraction_stats.log"
    
    print("📁 Archivos de log:")
    print(f"   Errores de parsing: {'✅' if os.path.exists(parsing_log) else '❌'} {parsing_log}")
    print(f"   Estadísticas: {'✅' if os.path.exists(stats_log) else '❌'} {stats_log}")
    print()
    
    # Analizar cada tipo de log
    analyze_extraction_stats()
    analyze_parsing_errors()
    
    print("🎉 Análisis completado!")

if __name__ == "__main__":
    generate_summary_report() 
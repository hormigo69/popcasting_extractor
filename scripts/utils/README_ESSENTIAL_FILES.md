# Archivos Esenciales para Replicar la Base de Datos

Este directorio contiene los archivos esenciales para replicar y mantener la base de datos de Popcasting. Los archivos auxiliares de comprobación han sido eliminados para mantener el directorio limpio.

## Archivos Principales para Replicación de BDD

### 1. **consolidate_manual_episodes.py** (29KB)
- **Propósito**: Script principal para regenerar completamente la base de datos
- **Funcionalidad**: 
  - Consolida todos los episodios manuales en un archivo JSON
  - Regenera la base de datos desde cero
  - Incluye todos los episodios con datos completos
- **Uso**: Ejecutar para regenerar la BDD completa

### 2. **restore_episodes_0_to_20_links.py** (33KB)
- **Propósito**: Restaurar enlaces extras de episodios específicos
- **Funcionalidad**:
  - Restaura enlaces extras originales de episodios #3-#91
  - Limpia episodios sin enlaces (#42, #46, #48, #49, #70, #71)
  - Contiene 217 enlaces extras restaurados
- **Uso**: Ejecutar después de la regeneración para restaurar enlaces extras

### 3. **manual_update_web_playlist.py** (17KB)
- **Propósito**: Actualizar playlists manuales de episodios específicos
- **Funcionalidad**:
  - Contiene playlists corregidas para episodios problemáticos
  - Unifica todas las correcciones manuales de playlists
- **Uso**: Ejecutar para aplicar playlists manuales corregidas

### 4. **verify_podcasts_integrity.py** (15KB)
- **Propósito**: Verificar la integridad de la tabla podcasts
- **Funcionalidad**:
  - Detecta episodios faltantes
  - Verifica secuencia de fechas
  - Identifica campos obligatorios faltantes
- **Uso**: Ejecutar para verificar integridad de episodios

### 5. **verify_links_integrity.py** (13KB)
- **Propósito**: Verificar la integridad de enlaces
- **Funcionalidad**:
  - Verifica coherencia entre URLs de episodios y descargas
  - Detecta discrepancias en números de episodio
  - Valida enlaces de descarga faltantes
- **Uso**: Ejecutar para verificar integridad de enlaces

### 6. **backup_supabase.py** (10KB)
- **Propósito**: Crear backups de la base de datos Supabase
- **Funcionalidad**:
  - Exporta tablas a JSON y CSV
  - Genera resumen de backup
  - Incluye timestamp
- **Uso**: Ejecutar regularmente para crear backups

### 7. **restore_supabase.py** (9.3KB)
- **Propósito**: Restaurar backups de Supabase
- **Funcionalidad**:
  - Restaura datos desde archivos de backup
  - Valida integridad de datos restaurados
- **Uso**: Ejecutar para restaurar desde backup

### 8. **optimize_database_types.py** (8.9KB)
- **Propósito**: Optimizar tipos de datos en la base de datos
- **Funcionalidad**:
  - Convierte campos de texto a tipos apropiados
  - Optimiza program_number (TEXT → INTEGER)
  - Optimiza date (TEXT → DATE)
- **Uso**: Ejecutar para optimizar tipos de datos

## Archivos de Soporte

### Análisis y Diagnóstico
- **diagnose_supabase_data.py**: Diagnóstico de datos en Supabase
- **analyze_songs_distribution.py**: Análisis de distribución de canciones
- **analyze_date_sequence.py**: Análisis de secuencia de fechas
- **investigate_duplicate_dates.py**: Investigación de fechas duplicadas

### Extracción y Migración
- **extract_playlists_from_wordpress_*.py**: Varios scripts para extraer playlists
- **migrate_web_songs_count.py**: Migración del campo web_songs_count
- **update_web_songs_count.py**: Actualización del campo web_songs_count
- **normalize_supabase_dates.py**: Normalización de fechas en Supabase

### Corrección de Datos
- **clean_duplicate_episodes.py**: Limpieza de episodios duplicados
- **fix_playlist_parsing.py**: Corrección de parsing de playlists
- **fix_single_song_episodes.py**: Corrección de episodios con una canción
- **fix_two_song_episodes.py**: Corrección de episodios con dos canciones
- **fix_low_songs_episodes.py**: Corrección de episodios con pocas canciones

### Utilidades
- **setup_smart_precommit.py**: Configuración de pre-commit hooks
- **smart_commit.py**: Commit inteligente
- **commit_without_linting.py**: Commit sin linting
- **fix_all_linting.py**: Corrección de errores de linting
- **fix_syntax_errors.py**: Corrección de errores de sintaxis

## Orden de Ejecución para Replicación

1. **backup_supabase.py** - Crear backup antes de empezar
2. **consolidate_manual_episodes.py** - Regenerar BDD completa
3. **restore_episodes_0_to_20_links.py** - Restaurar enlaces extras
4. **manual_update_web_playlist.py** - Aplicar playlists manuales
5. **optimize_database_types.py** - Optimizar tipos de datos
6. **verify_podcasts_integrity.py** - Verificar integridad de episodios
7. **verify_links_integrity.py** - Verificar integridad de enlaces

## Archivos de Logs Esenciales

- **restore_episodes_links_final_summary.txt**: Resumen final de restauración de enlaces
- **parsing_errors.log**: Errores de parsing (mantener para debugging)
- **extraction_stats.log**: Estadísticas de extracción (mantener para análisis)

## Notas

- Los archivos auxiliares de comprobación han sido eliminados para mantener el directorio limpio
- Solo se mantienen los archivos esenciales para replicar y mantener la base de datos
- El archivo `restore_episodes_0_to_20_links.py` contiene la versión final con todos los enlaces extras restaurados
- Todos los scripts están optimizados y listos para uso en producción 
# Regeneración de la Base de Datos

Este documento describe cómo regenerar la base de datos Supabase desde cero, incluyendo los episodios que no se extraen del RSS.

## Archivos Esenciales

### 📁 `data/manual_episodes.json`
Contiene todos los episodios que no se extraen del RSS y requieren inserción manual:
- **13 episodios** con datos completos (título, fecha, URLs, playlist, etc.)
- **Episodios incluidos**: #82, #83, #92, #93, #97, #99, #100, #102, #103, #104, #105, #106, #148
- **Formato**: JSON estructurado con todos los campos necesarios

### 🔧 Scripts Principales

#### `scripts/utils/consolidate_manual_episodes.py`
- **Propósito**: Genera el archivo `manual_episodes.json` con todos los episodios manuales
- **Uso**: `python scripts/utils/consolidate_manual_episodes.py`
- **Funcionalidad**: 
  - Define todos los episodios manuales con sus datos completos
  - Guarda en JSON para uso posterior
  - Opción de inserción directa en BDD

#### `scripts/utils/insert_manual_episodes.py`
- **Propósito**: Inserta episodios manuales desde el archivo JSON
- **Uso**: `python scripts/utils/insert_manual_episodes.py`
- **Funcionalidad**:
  - Carga episodios desde `manual_episodes.json`
  - Inserta en Supabase con canciones y links extras
  - Confirmación antes de inserción

#### `scripts/utils/verify_podcasts_integrity.py`
- **Propósito**: Verifica la integridad de la tabla podcasts
- **Uso**: `python scripts/utils/verify_podcasts_integrity.py`
- **Funcionalidad**:
  - Verifica números de capítulo faltantes
  - Verifica secuencia de fechas
  - Verifica campos obligatorios
  - Genera reporte detallado

## Proceso de Regeneración

### 1. Extracción desde RSS
```bash
# Ejecutar el extractor principal para obtener episodios del RSS
python main.py
```

### 2. Inserción de Episodios Manuales
```bash
# Insertar episodios que no están en el RSS
python scripts/utils/insert_manual_episodes.py
```

### 3. Verificación de Integridad
```bash
# Verificar que todo esté correcto
python scripts/utils/verify_podcasts_integrity.py
```

## Estado Esperado

Después de la regeneración completa, deberías tener:
- **485 episodios** (del #0 al #484)
- **0 problemas de integridad**
- **Secuencia de fechas perfecta**
- **Todos los campos obligatorios presentes**

## Episodios Manuales Incluidos

| # | Título | Fecha | Canciones |
|---|--------|-------|----------|
| 82 | Popcasting #082 | 2008-11-01 | 10 |
| 83 | Popcasting #83 | 2008-11-15 | 10 |
| 92 | Popcasting #92 | 2009-04-01 | 12 |
| 93 | Popcasting #93 | 2009-04-11 | 11 |
| 97 | Popcasting #97 | 2009-06-15 | 11 |
| 99 | Popcasting #99 | 2009-07-15 | 10 |
| 100 | Popcasting #100 | 2009-08-01 | 12 |
| 102 | Popcasting #102 | 2009-09-01 | 12 |
| 103 | Popcasting #103 | 2009-09-15 | 20 |
| 104 | Popcasting #104 | 2009-10-01 | 10 |
| 105 | Popcasting #105 | 2009-10-15 | 13 |
| 106 | Popcasting #106 | 2009-11-01 | 11 |
| 148 | Popcasting #148 | 2011-08-01 | 18 |

## Notas Importantes

- Los episodios manuales tienen fechas corregidas para mantener la secuencia quincenal
- El episodio #82 tiene fecha 2008-11-01 (no 2015-08-05 como aparecía originalmente)
- Todos los episodios incluyen playlists completas y URLs de descarga
- La colección está completa sin gaps artificiales en la numeración

## Scripts de Mantenimiento

### Limpieza de Duplicados
```bash
python scripts/utils/clean_duplicate_episodes.py
```

### Diagnóstico de Datos
```bash
python scripts/utils/diagnose_supabase_data.py
```

### Backup de Supabase
```bash
python scripts/utils/backup_supabase.py
``` 
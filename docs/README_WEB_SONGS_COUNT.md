# Campo web_songs_count

## Descripción

Se ha añadido un nuevo campo `web_songs_count` a la tabla `podcasts` para almacenar el número de canciones extraído automáticamente del campo `web_playlist`.

## Características

- **Campo**: `web_songs_count` (INTEGER)
- **Origen**: Calculado automáticamente desde `web_playlist` (JSON)
- **Compatibilidad**: SQLite y Supabase
- **Actualización automática**: Se calcula cada vez que se extrae información web

## Implementación

### Base de Datos

#### SQLite
- El campo se añade automáticamente al inicializar la base de datos
- Migración automática en `services/database.py`

#### Supabase
- Script SQL: `migration/add_web_songs_count_field.sql`
- Índice creado para optimizar consultas
- Ejecutar manualmente en el SQL Editor de Supabase

### Código

#### Funciones actualizadas
- `update_web_info()` en `services/database.py` y `services/supabase_database.py`
- `WebExtractor.extract_all_web_info()` en `services/web_extractor.py`
- `extract_web_info()` en `services/web_cli.py`

#### Scripts de migración
- `scripts/utils/migrate_web_songs_count.py`: Migración completa
- `scripts/utils/update_web_songs_count.py`: Actualización de episodios existentes

## Uso

### Migración inicial

```bash
# Ejecutar migración completa
python scripts/utils/migrate_web_songs_count.py

# O ejecutar manualmente:
# 1. Ejecutar migration/add_web_songs_count_field.sql en Supabase
# 2. python scripts/utils/update_web_songs_count.py
```

### Verificar el campo

```bash
# Ver información de un episodio específico
python -m services.web_cli info <episode_id>

# Ejemplo de salida:
#   Número de canciones (web_songs_count): 15
```

### Consultas SQL

```sql
-- Episodios con más canciones
SELECT program_number, title, web_songs_count 
FROM podcasts 
WHERE web_songs_count IS NOT NULL 
ORDER BY web_songs_count DESC;

-- Estadísticas de canciones por episodio
SELECT 
    AVG(web_songs_count) as promedio_canciones,
    MIN(web_songs_count) as min_canciones,
    MAX(web_songs_count) as max_canciones,
    COUNT(*) as episodios_con_playlist
FROM podcasts 
WHERE web_songs_count IS NOT NULL;
```

## Ventajas

1. **Rendimiento**: Evita parsear JSON en cada consulta
2. **Estadísticas**: Facilita análisis de número de canciones por episodio
3. **Validación**: Permite verificar integridad de datos
4. **Búsqueda**: Índice optimizado para consultas por número de canciones

## Mantenimiento

### Actualización automática
El campo se actualiza automáticamente cuando:
- Se extrae información web de un episodio
- Se ejecuta el extractor web
- Se procesa un episodio específico

### Actualización manual
Para episodios existentes sin el campo:

```bash
python scripts/utils/update_web_songs_count.py
```

## Verificación

### Script de verificación
```bash
python scripts/utils/update_web_songs_count.py
```

### Salida esperada
```
📊 Estadísticas de web_songs_count:
   Episodios con web_songs_count: 363
   Episodios sin web_songs_count: 33
   Total de canciones contadas: 5432
   Promedio de canciones por episodio: 15.0
```

## Resultados de la implementación

### ✅ **Estado actual**
- **Episodios procesados**: 485 episodios
- **Episodios con web_songs_count**: En proceso de actualización
- **Rango de canciones**: 11-36 canciones por episodio
- **Promedio estimado**: ~15-20 canciones por episodio

### 📊 **Ejemplos de episodios actualizados**
- Episodio #484: 27 canciones
- Episodio #483: 36 canciones
- Episodio #482: 32 canciones
- Episodio #481: 17 canciones
- Episodio #480: 20 canciones

### 🔧 **Funcionalidad activa**
- ✅ Campo añadido a la base de datos
- ✅ Cálculo automático en extracción web
- ✅ Scripts de migración funcionando
- ✅ CLI actualizado para mostrar el campo

## Compatibilidad

- ✅ SQLite
- ✅ Supabase (PostgreSQL)
- ✅ WebExtractor
- ✅ CLI web
- ✅ Scripts de migración
- ✅ Scripts de extracción masiva

## Archivos modificados

- `migration/add_web_songs_count_field.sql` (nuevo)
- `migration/supabase_schema.sql`
- `services/database.py`
- `services/supabase_database.py`
- `services/web_extractor.py`
- `services/web_cli.py`
- `scripts/reports/batch_web_extraction.py`
- `scripts/utils/migrate_web_songs_count.py` (nuevo)
- `scripts/utils/update_web_songs_count.py` (nuevo)
- `docs/technical/TODOs.md`
- `docs/README_WEB_SONGS_COUNT.md` (nuevo) 
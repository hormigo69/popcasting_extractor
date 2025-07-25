# 🎵 Extracción de Duración de Audio MP3

Este módulo permite extraer la duración de archivos MP3 desde el NAS Synology y actualizar la base de datos Supabase con esta información.

## 📋 Características

- ✅ **Extracción automática**: Usa Mutagen para extraer duración de archivos MP3
- ✅ **Integración completa**: Conecta con Supabase y Synology NAS
- ✅ **Procesamiento en lotes**: Puede procesar múltiples episodios
- ✅ **Manejo de errores**: Logs detallados y recuperación de errores
- ✅ **Context manager**: Manejo automático de conexiones y limpieza
- ✅ **Reportes completos**: Genera logs JSON y resúmenes en texto

## 🔧 Instalación

### Dependencias

```bash
# Activar entorno virtual
source .venv/bin/activate

# Instalar Mutagen
pip install mutagen
```

### Configuración

Asegúrate de que las variables de entorno estén configuradas:

```env
# Supabase
DATABASE_TYPE=supabase
supabase_project_url=tu_url_de_supabase
supabase_api_key=tu_api_key_de_supabase

# Synology NAS
SYNOLOGY_IP=192.168.1.100
SYNOLOGY_PORT=5000
SYNOLOGY_USER=tu_usuario
SYNOLOGY_PASS=tu_contraseña
```

## 🚀 Uso

### Uso Básico

```python
from services.audio_duration_extractor import AudioDurationExtractor

# Usar context manager (recomendado)
with AudioDurationExtractor() as extractor:
    # Procesar todos los episodios sin duración
    results = extractor.process_all_episodes_without_duration()
    
    # Generar reporte
    report = extractor.generate_report(results)
    print(f"Procesados {report['metadata']['total_episodes']} episodios")
```

### Uso Manual

```python
from services.audio_duration_extractor import AudioDurationExtractor

# Crear instancia
extractor = AudioDurationExtractor()

# Conectar manualmente
extractor.synology = SynologyClient()
extractor.synology.login()

# Procesar episodio específico
result = extractor.process_single_episode(482)
print(f"Éxito: {result['success']}, Duración: {result['duration']}")

# Cerrar conexión
extractor.synology.logout()
```

### Script de Línea de Comandos

```bash
# Procesar todos los episodios sin duración
python scripts/utils/extract_audio_duration.py

# Pruebas
python tests/test_audio_duration.py
python tests/test_audio_duration_3_files.py
python tests/test_mutagen_extraction.py
```

## 📊 Estructura de la Clase

### AudioDurationExtractor

#### Métodos Principales

- `process_all_episodes_without_duration()`: Procesa todos los episodios sin duración
- `process_single_episode(program_number)`: Procesa un episodio específico
- `process_multiple_episodes(program_numbers)`: Procesa múltiples episodios
- `generate_report(results)`: Genera reporte de resultados

#### Métodos de Utilidad

- `get_podcasts_without_duration()`: Obtiene episodios sin duración
- `get_podcast_by_program_number(program_number)`: Busca episodio por número
- `download_mp3_from_synology(program_number)`: Descarga MP3 del NAS
- `extract_duration_from_mp3(mp3_path)`: Extrae duración con Mutagen
- `update_podcast_duration(podcast_id, duration)`: Actualiza Supabase

## 📁 Estructura de Archivos

```
services/
├── audio_duration_extractor.py    # Clase principal
└── __init__.py                    # Importaciones

scripts/utils/
└── extract_audio_duration.py      # Script principal

tests/
├── test_audio_duration.py         # Pruebas básicas
├── test_audio_duration_3_files.py # Pruebas con archivos
└── test_mutagen_extraction.py     # Pruebas de Mutagen

docs/
└── README_AUDIO_DURATION.md       # Esta documentación
```

## 📝 Logs y Reportes

### Formato de Log JSON

```json
{
  "metadata": {
    "total_episodes": 10,
    "successful": 8,
    "failed": 2,
    "success_rate": 80.0,
    "total_duration_seconds": 7200,
    "total_processing_time": 45.2,
    "timestamp": "2025-01-27T10:30:00"
  },
  "results": [
    {
      "program_number": 482,
      "success": true,
      "duration": 3600,
      "error": null,
      "processing_time": 4.5
    }
  ]
}
```

### Archivos Generados

- `logs/audio_duration_extraction_YYYYMMDD_HHMMSS.json`: Log detallado
- `logs/audio_duration_extraction_YYYYMMDD_HHMMSS_summary.txt`: Resumen en texto

## 🧪 Pruebas

### Prueba Básica

```bash
python tests/test_audio_duration.py
```

Verifica:
- ✅ Conexión a Supabase
- ✅ Obtención de episodios sin duración
- ✅ Importación de Mutagen

### Prueba con 3 Archivos

```bash
python tests/test_audio_duration_3_files.py
```

Procesa 3 episodios reales para verificar:
- ✅ Descarga desde Synology
- ✅ Extracción de duración
- ✅ Actualización en Supabase

### Prueba de Mutagen

```bash
python tests/test_mutagen_extraction.py
```

Prueba específicamente:
- ✅ Importación de Mutagen
- ✅ Extracción de duración de MP3
- ✅ Manejo de errores
- ✅ Formatos múltiples

## 🔍 Solución de Problemas

### Error de Conexión a Supabase

```
❌ Error obteniendo episodios sin duración: [Error de conexión]
```

**Solución**: Verifica las variables de entorno de Supabase en `.env`

### Error de Conexión a Synology

```
❌ No se pudo conectar al NAS Synology
```

**Solución**: Verifica las variables de entorno del NAS en `.env`

### Error de Mutagen

```
❌ Error extrayendo duración: [Error de Mutagen]
```

**Solución**: 
1. Verifica que Mutagen esté instalado: `pip install mutagen`
2. Verifica que el archivo MP3 sea válido
3. Ejecuta: `python tests/test_mutagen_extraction.py`

### Error de Descarga

```
❌ Error descargando MP3 del episodio #482
```

**Solución**:
1. Verifica que el archivo existe en el NAS
2. Verifica permisos de usuario en Synology
3. Verifica conectividad de red

## 📈 Estadísticas

### Campos Actualizados

- **duration**: Duración en segundos (INTEGER)
- **updated_at**: Timestamp de actualización

### Ejemplo de Datos

```sql
-- Episodio con duración
SELECT program_number, title, duration, 
       duration/60 as minutes, 
       duration%60 as seconds
FROM podcasts 
WHERE duration IS NOT NULL 
LIMIT 5;
```

## 🔄 Flujo de Trabajo

1. **Identificación**: Busca episodios sin duración en Supabase
2. **Descarga**: Descarga MP3 desde Synology NAS
3. **Extracción**: Usa Mutagen para extraer duración
4. **Actualización**: Actualiza campo `duration` en Supabase
5. **Limpieza**: Elimina archivos temporales
6. **Reporte**: Genera logs y resúmenes

## 🎯 Casos de Uso

### Procesamiento Completo

```python
# Procesar todos los episodios sin duración
with AudioDurationExtractor() as extractor:
    results = extractor.process_all_episodes_without_duration()
```

### Procesamiento Selectivo

```python
# Procesar episodios específicos
episodes_to_process = [482, 483, 484]
with AudioDurationExtractor() as extractor:
    results = extractor.process_multiple_episodes(episodes_to_process)
```

### Verificación

```python
# Verificar episodios sin duración
extractor = AudioDurationExtractor()
episodes_without_duration = extractor.get_podcasts_without_duration()
print(f"Episodios sin duración: {len(episodes_without_duration)}")
```

## 🔧 Configuración Avanzada

### Personalizar Rutas

```python
# Cambiar carpeta de destino en Synology
extractor.download_mp3_from_synology(482, "/otra_carpeta/mp3")

# Cambiar directorio temporal
extractor.temp_dir = Path("/tmp/audio_duration")
```

### Logging Personalizado

```python
# Configurar logging personalizado
import logging
logging.basicConfig(level=logging.DEBUG)

# Usar extractor con logging detallado
with AudioDurationExtractor() as extractor:
    # El logging se mostrará automáticamente
    results = extractor.process_all_episodes_without_duration()
```

## 📚 Referencias

- [Mutagen Documentation](https://mutagen.readthedocs.io/)
- [Supabase Python Client](https://supabase.com/docs/reference/python)
- [Synology API Documentation](https://developer.synology.com/)

## 🤝 Contribución

Para contribuir a este módulo:

1. Ejecuta las pruebas: `python tests/test_audio_duration.py`
2. Verifica el código: `python -m flake8 services/audio_duration_extractor.py`
3. Documenta cambios en `docs/README_AUDIO_DURATION.md`

## 📄 Licencia

Este módulo es parte del proyecto Popcasting Extractor y sigue la misma licencia. 
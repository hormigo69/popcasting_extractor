# Changelog

## [Unreleased] - 2025-07-26

### ✨ Nuevas Funcionalidades

#### AudioManager - Extracción de Duración MP3
- **Nueva funcionalidad**: Extracción automática de duración exacta de archivos MP3
- **Integración**: El AudioManager ahora extrae la duración real del archivo descargado
- **Base de datos**: Nuevo campo `mp3_duration` en la tabla `podcasts`
- **Lógica de prioridad**: MP3 extraído > duración RSS > warning si no hay duración

#### Mejoras Técnicas
- **ffprobe integration**: Uso de ffprobe para análisis preciso de archivos multimedia
- **Manejo de errores**: Timeouts, parsing JSON, archivos corruptos
- **Logging mejorado**: Información detallada sobre el proceso de extracción
- **Compatibilidad**: No afecta el flujo existente, integración transparente

### 🔧 Cambios Técnicos

#### Dependencias
- Añadida `ffmpeg-python` para análisis de archivos multimedia
- Eliminada `ffprobe-python` (incompatible con Python 3.13)

#### DatabaseManager
- Nuevo método `update_podcast_mp3_duration(podcast_id, duration_in_seconds)`
- Conversión automática a segundos enteros para compatibilidad con BD

#### AudioManager
- Nuevo método privado `_get_duration_from_mp3(file_path)`
- Integración en `archive_podcast_audio()` después de descargar el MP3
- Redondeo a segundos enteros para almacenamiento en BD

### 🧪 Pruebas

#### Scripts de Prueba Creados
- `tests/test_audio_duration.py` - Prueba básica de extracción
- `tests/test_audio_manager_complete.py` - Prueba completa del flujo

#### Verificación
- ✅ Extracción de duración funciona correctamente
- ✅ Guardado en BD funciona
- ✅ Manejo de errores implementado
- ✅ Compatibilidad con flujo existente

### 📚 Documentación

#### Archivos Creados/Actualizados
- `docs/AUDIO_MANAGER_IMPROVEMENTS.md` - Documentación detallada de mejoras
- `README.md` - Actualizado con nuevas funcionalidades
- `CHANGELOG.md` - Este archivo

### 🔄 Flujo de Trabajo

El AudioManager ahora:
1. **Descarga** el archivo MP3 del podcast
2. **Extrae** la duración exacta usando ffprobe
3. **Aplica** lógica de prioridad (MP3 > RSS)
4. **Guarda** la duración en el campo `mp3_duration` de la BD
5. **Continúa** con el proceso normal (subida al NAS)

### 📋 Requisitos del Sistema

- **ffprobe**: Instalado en el sistema (disponible con ffmpeg)
- **Supabase**: Conexión para guardar la duración
- **Campo BD**: `mp3_duration` en la tabla `podcasts` (tipo integer)

### 🎯 Resultado

- **Precisión**: Duración exacta extraída del archivo MP3 real
- **Automatización**: Proceso transparente sin cambios en el flujo existente
- **Robustez**: Manejo de errores para evitar interrupciones
- **Compatibilidad**: Funciona con cualquier archivo MP3 válido

---

## [Anterior] - 2025-07-XX

### Funcionalidades Base
- Sincronización RSS con Supabase
- Integración con WordPress
- Procesamiento de playlists
- Gestión de archivos en NAS Synology 
# AudioManager - Gestor de Audio para Podcasts

Componente especializado para gestionar la descarga de archivos MP3 de podcasts y su subida al NAS Synology.

## 🎯 Características

- ✅ **Descarga automática** de archivos MP3 desde URLs de podcasts
- ✅ **Subida al NAS** Synology usando la API de File Station
- ✅ **Actualización de base de datos** con las rutas del NAS
- ✅ **Limpieza automática** de archivos temporales
- ✅ **Context manager** para manejo seguro de recursos
- ✅ **Logging detallado** de todas las operaciones
- ✅ **Manejo de errores** robusto

## 📋 Prerrequisitos

### 1. Configuración de la base de datos

No se requiere migración adicional. El componente genera las rutas del NAS dinámicamente basándose en el número de programa del podcast.

### 2. Configuración del NAS Synology

Asegúrate de tener configuradas las variables de entorno en el archivo `.env`:

```env
SYNOLOGY_IP=192.168.1.143
SYNOLOGY_PORT=5000
SYNOLOGY_USER=popcasting
SYNOLOGY_PASS=tu_contraseña
```

### 3. Dependencias

El proyecto ya incluye las dependencias necesarias:
- `requests` - Para descargas HTTP
- `pathlib` - Para manejo de rutas
- `shutil` - Para limpieza de archivos

## 🚀 Uso básico

### Importar el componente

```python
from src.components.audio_manager import AudioManager
from services.supabase_database import SupabaseDatabase
from synology.synology_client import SynologyClient
```

### Uso manual

```python
# Inicializar componentes
db_manager = SupabaseDatabase()
synology_client = SynologyClient()

# Autenticar con Synology
if synology_client.login():
    # Crear AudioManager
    audio_manager = AudioManager(db_manager, synology_client)
    
    # Archivar audio de un podcast
    podcast_id = 123
    success = audio_manager.archive_podcast_audio(podcast_id)
    
    if success:
        print("✅ Podcast archivado exitosamente")
    
    # Limpiar
    audio_manager.cleanup_temp_folder()
    synology_client.logout()
```

### Uso con context manager (recomendado)

```python
# Inicializar componentes
db_manager = SupabaseDatabase()
synology_client = SynologyClient()

if synology_client.login():
    with AudioManager(db_manager, synology_client) as audio_manager:
        # Archivar audio de un podcast
        podcast_id = 123
        success = audio_manager.archive_podcast_audio(podcast_id)
        
        if success:
            print("✅ Podcast archivado exitosamente")
    
    synology_client.logout()
```

## 📚 Métodos disponibles

### `__init__(database_manager, synology_client)`

Inicializa el AudioManager.

**Args:**
- `database_manager`: Instancia de DatabaseManager
- `synology_client`: Instancia de SynologyClient

### `archive_podcast_audio(podcast_id: int) -> bool`

Método principal para archivar el audio de un podcast.

**Args:**
- `podcast_id`: ID del podcast a procesar

**Returns:**
- `bool`: True si el proceso fue exitoso

**Flujo del proceso:**
1. Obtiene información del podcast desde la BD
2. Verifica que el archivo no exista ya en el NAS
3. Descarga el archivo MP3 a carpeta temporal
4. Sube el archivo al NAS Synology con nombre `popcasting_XXXX.mp3`
5. Limpia archivos temporales

### `_download_file(url: str, destination_folder: Path) -> Optional[Path]`

Método privado para descargar archivos.

**Args:**
- `url`: URL del archivo a descargar
- `destination_folder`: Carpeta de destino

**Returns:**
- `Path`: Ruta del archivo descargado o None si falla

### `_cleanup_temp_file(file_path: Path) -> None`

Elimina un archivo temporal.

### `cleanup_temp_folder() -> None`

Limpia toda la carpeta temporal de descargas.

### `get_nas_path_for_podcast(program_number: int) -> str`

Genera la ruta del NAS para un podcast basado en su número de programa.

**Args:**
- `program_number`: Número del programa

**Returns:**
- `str`: Ruta completa del archivo en el NAS

### `check_podcast_in_nas(program_number: int) -> bool`

Verifica si un podcast existe en el NAS basado en su número de programa.

**Args:**
- `program_number`: Número del programa

**Returns:**
- `bool`: True si el archivo existe en el NAS

## 🔧 Configuración avanzada

### Carpeta de destino en el NAS

Por defecto, los archivos se suben a `/popcasting_marilyn/mp3s`. Puedes modificar esto en el método `archive_podcast_audio`:

```python
# Cambiar la carpeta de destino
nas_folder = "/tu_carpeta_personalizada/mp3s"
```

### Carpeta temporal local

Por defecto, se usa `temp_downloads` en el directorio actual. Puedes modificar esto en el constructor:

```python
class AudioManager:
    def __init__(self, database_manager, synology_client, temp_folder="mi_carpeta_temp"):
        self.temp_downloads = Path(temp_folder)
```

## 📊 Procesamiento por lotes

Para procesar múltiples podcasts:

```python
# Obtener podcasts con URL de descarga
all_podcasts = db_manager.get_all_podcasts()
podcasts_to_process = [
    p for p in all_podcasts 
    if p.get('download_url') and p.get('program_number')
]

with AudioManager(db_manager, synology_client) as audio_manager:
    for podcast in podcasts_to_process:
        success = audio_manager.archive_podcast_audio(podcast['id'])
        if success:
            print(f"✅ {podcast['title']} archivado")
        else:
            print(f"❌ Error con {podcast['title']}")
```

## 🔍 Verificación de archivos en el NAS

Para verificar qué podcasts están en el NAS:

```python
with AudioManager(db_manager, synology_client) as audio_manager:
    for podcast in podcasts:
        program_number = podcast.get('program_number')
        if program_number:
            exists = audio_manager.check_podcast_in_nas(program_number)
            nas_path = audio_manager.get_nas_path_for_podcast(program_number)
            status = "✅ Existe" if exists else "❌ No existe"
            print(f"{program_number:3d} - {podcast['title']} {status}")
            print(f"   Ruta: {nas_path}")
```

## Optimización de comprobación de archivos en NAS

A partir de la versión actual, la comprobación de si un archivo MP3 ya existe en el NAS se realiza usando el método `getinfo` de la API de Synology, en vez de listar todos los archivos de la carpeta. Esto hace que la comprobación sea mucho más eficiente y elimina los logs masivos de archivos.

**Ventajas:**
- Solo se consulta la API para el archivo concreto
- El proceso es mucho más rápido
- Los logs son limpios y claros

**Código relevante:**
```python
# Antes:
files = synology_client.list_files(folder)
# Ahora:
exists = synology_client.file_exists(remote_path)
```

---

## 🧪 Pruebas

Ejecuta las pruebas del componente:

```bash
# Desde el directorio raíz del proyecto
python tests/test_audio_manager.py
```

O ejecuta el ejemplo de uso:

```bash
python src/components/example_audio_manager.py
```

## 📝 Logs

El componente genera logs detallados de todas las operaciones:

```
🔄 Iniciando archivo de audio para podcast ID: 123
📥 Descargando desde: https://example.com/podcast.mp3
✅ Archivo descargado: temp_downloads/podcast.mp3
✅ Archivo subido al NAS: /popcasting_marilyn/mp3s/podcast.mp3
✅ Base de datos actualizada con ruta del NAS
🗑️ Archivo temporal eliminado: temp_downloads/podcast.mp3
🎉 Proceso completado exitosamente para podcast 123
```

## ⚠️ Consideraciones

### Espacio en disco

- Los archivos se descargan temporalmente al disco local
- Se limpian automáticamente después de la subida
- Asegúrate de tener suficiente espacio libre

### Tiempo de descarga

- Las descargas pueden tardar dependiendo del tamaño del archivo
- Se usa un timeout de 5 minutos por descarga
- Los archivos grandes pueden requerir más tiempo

### Conexión de red

- Requiere conexión estable a internet para descargas
- Requiere conexión al NAS Synology para subidas
- Maneja automáticamente errores de red

## 📁 Estructura de archivos en el NAS

Los archivos se almacenan en el NAS con la siguiente estructura:

### Ubicación
```
/popcasting_marilyn/mp3/
```

### Convención de nombres
```
popcasting_0001.mp3  # Episodio 1
popcasting_0042.mp3  # Episodio 42
popcasting_0100.mp3  # Episodio 100
popcasting_0999.mp3  # Episodio 999
```

### Verificación

Puedes verificar si un podcast está en el NAS:

```python
audio_manager = AudioManager(db_manager, synology_client)
program_number = 42
exists = audio_manager.check_podcast_in_nas(program_number)
nas_path = audio_manager.get_nas_path_for_podcast(program_number)

if exists:
    print(f"✅ Episodio {program_number} existe en: {nas_path}")
else:
    print(f"❌ Episodio {program_number} no está en el NAS")
```

## 🎉 Ejemplos completos

Consulta el archivo `example_audio_manager.py` para ejemplos completos de uso, incluyendo:

- Uso básico del componente
- Procesamiento por lotes
- Manejo de errores
- Verificación de resultados

## ✅ Estado del Proyecto

### Implementación Completada

- ✅ **AudioManager implementado y probado exitosamente**
- ✅ **Descarga y subida de archivos MP3 funcionando perfectamente**
- ✅ **Renombrado automático al formato correcto `popcasting_XXXX.mp3`**
- ✅ **Verificación de existencia en NAS para evitar duplicados**
- ✅ **Limpieza automática de archivos temporales**
- ✅ **Logging completo y manejo de errores robusto**
- ✅ **Integración completa con Supabase y Synology NAS**

### Pruebas Realizadas

- ✅ **Prueba unitaria**: Descarga del episodio 485
- ✅ **Verificación**: Archivo subido correctamente como `popcasting_0485.mp3`
- ✅ **Estado final**: 475 episodios completos en el NAS (0-485)
- ✅ **Corrección**: Límite de paginación en SynologyClient aumentado a 1000 archivos
- ✅ **Optimización**: Renombrado automático antes de subida al NAS

### Estado Actual del Catálogo

- **Total de episodios en base de datos**: 486
- **Episodios con URL de descarga**: 475
- **Episodios descargados en NAS**: 475 (0-485)
- **Episodio más alto**: 485
- **Episodio más bajo**: 0

El componente está **listo para producción** y puede manejar automáticamente la descarga y subida de cualquier episodio que falte en el futuro. 
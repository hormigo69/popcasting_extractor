# Popcasting Extractor

Extractor de podcasts de Popcasting con funcionalidad de archivado automático de audio.

## Características

- **Extracción de RSS**: Descarga automática de episodios desde feeds RSS
- **Procesamiento de canciones**: Extracción y almacenamiento de playlists
- **Base de datos**: Soporte para SQLite y Supabase
- **Archivado de audio**: Descarga automática y subida al NAS Synology
- **Extracción de duración**: Análisis automático de duración de episodios
- **Control de cambios**: Solo actualiza contenido modificado

## Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```bash
# Base de datos
DATABASE_TYPE=supabase
supabase_project_url=tu_url_de_supabase
supabase_api_key=tu_api_key_de_supabase

# Synology NAS (para archivado de audio)
SYNOLOGY_IP=192.168.1.100
SYNOLOGY_PORT=5000
SYNOLOGY_USER=tu_usuario
SYNOLOGY_PASS=tu_contraseña
```

### Instalación

1. Clona el repositorio
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Configura las variables de entorno
4. Ejecuta el extractor:
   ```bash
   python main.py
   ```

## Funcionalidades

### Extracción de Episodios

El sistema extrae automáticamente:
- Información del episodio (título, fecha, URL)
- Playlist de canciones
- Enlaces de descarga
- Duración del audio

### Archivado de Audio

Para cada episodio procesado:
1. Descarga el archivo MP3 desde iVoox
2. Lo renombra al formato estándar (`popcasting_XXXX.mp3`)
3. Lo sube al NAS Synology en `/popcasting_marilyn/mp3/`
4. Limpia los archivos temporales

### Base de Datos

Soporte para dos tipos de base de datos:
- **Supabase** (recomendado): Base de datos en la nube
- **SQLite**: Base de datos local

## Estructura del Proyecto

```
popcasting_extractor/
├── main.py                 # Punto de entrada principal
├── services/              # Servicios principales
│   ├── popcasting_extractor.py
│   ├── config.py
│   ├── config_manager.py
│   └── ...
├── src/components/        # Componentes reutilizables
│   ├── audio_manager.py   # Gestor de audio
│   └── ...
├── synology/             # Cliente para Synology NAS
│   └── synology_client.py
├── tests/                # Pruebas
└── docs/                 # Documentación
```

## Pruebas

Ejecuta las pruebas de integración:

```bash
python tests/test_audio_integration.py
```

## Logs

El sistema genera logs detallados:
- `logs/extraction_stats.log`: Estadísticas de extracción
- `logs/parsing_errors.log`: Errores de parsing

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. 
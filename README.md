# Extractor de WordPress para Popcasting

Extractor independiente para procesar episodios de Popcasting desde la API de WordPress.com, con integración a Supabase y almacenamiento en NAS Synology.

## 🎙️ RSS Feed Generado

Este proyecto también incluye un **feed RSS generado automáticamente** desde Supabase:

- **URL**: `https://ndhmlymnbrewflharfmr.supabase.co/functions/v1/rss`
- **Episodios**: 486 (todos los episodios)
- **Formato**: RSS 2.0 + iTunes completo
- **Plataformas**: iTunes, Spotify, Google Podcasts

📖 **Documentación RSS**: [`docs/RSS_FEED_SETUP.md`](docs/RSS_FEED_SETUP.md)  
⚡ **Quick Start RSS**: [`README_RSS.md`](README_RSS.md)

## 🎯 Propósito

Este extractor está diseñado para:
- **Leer episodios desde la API de WordPress.com**
- Extraer información completa de episodios y canciones
- Sincronizar datos con Supabase
- **Procesar playlists de canciones desde el contenido HTML**
- Procesar y normalizar datos de forma automática
- **Descargar archivos MP3 y extraer duración exacta**
- **Subir archivos al NAS Synology**
- **Gestionar metadatos de audio de forma precisa**

## 📁 Estructura del Proyecto

```
popcasting_extractor/
├── README.md                     # Este archivo
├── config.ini                    # Configuración del extractor
├── requirements.txt              # Dependencias Python
├── docs/                         # Documentación técnica
├── logs/                         # Archivos de log
├── tests/                        # Scripts de prueba
└── src/
    ├── components/               # Componentes principales
    │   ├── config_manager.py     # Gestor de configuración
    │   ├── database_manager.py   # Gestor de base de datos
    │   ├── song_processor.py     # Procesador de canciones
    │   ├── audio_manager.py      # Gestor de audio (descarga + duración)
    │   ├── synology_client.py    # Cliente para NAS Synology
    │   └── synology_uploader.py  # Subidor de archivos al NAS
    ├── api/                      # APIs externas
    │   └── wpcom_api.py          # API de WordPress.com
    ├── utils/                    # Utilidades
    │   └── logger.py             # Sistema de logging
    └── main.py                   # Punto de entrada principal
```

## 🚀 Instalación

1. **Clonar o copiar el proyecto**
2. **Instalar dependencias:**
   ```bash
   cd popcasting_extractor
   pip install -r requirements.txt
   ```

3. **Instalar ffprobe (requerido para extracción de duración de audio):**
   ```bash
   # macOS con Homebrew
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # Windows (usando Chocolatey)
   choco install ffmpeg
   ```

4. **Configurar variables de entorno:**
   - Crear archivo `.env` en el directorio raíz con las credenciales:
   ```env
   # Supabase
   supabase_project_url=https://tu-proyecto.supabase.co
   supabase_service_role=tu-service-role-key
   
   # Synology NAS
   SYNOLOGY_IP=192.168.1.143
   SYNOLOGY_PORT=5000
   SYNOLOGY_USER=usuario
   SYNOLOGY_PASS=contraseña
   SYNOLOGY_SHARED_FOLDER=/popcasting_marilyn
   ```

5. **Configurar config.ini:**
   - Editar `config.ini` con las URLs de WordPress

## 🧪 Prueba de Conexión

Para verificar que todo funciona correctamente:

```bash
# Prueba básica de conexión
python test_connection.py

# Prueba de extracción de duración de audio
python tests/test_audio_duration.py

# Prueba completa del AudioManager
python tests/test_audio_manager_complete.py
```

Estos scripts probarán:
- ✅ Carga de configuración
- ✅ Conexión a Supabase
- ✅ Lectura de credenciales
- ✅ Extracción de duración de archivos MP3
- ✅ Funcionalidad completa del AudioManager

## 📖 Documentación

- **`docs/`**: Documentación técnica detallada
  - `ARQUITECTURA.md`: Diseño del sistema
  - `INSTALACION.md`: Guía de instalación
  - `README_AUDIO_MANAGER.md`: Gestor de audio
  - `README_SYNOLOGY_CLIENT.md`: Cliente Synology
- **`logs/`**: Archivos de log para debugging
- **`config.ini`**: Configuración del sistema

## 🔧 Configuración

### Variables de Entorno Requeridas (.env)
- `supabase_project_url`: URL del proyecto Supabase
- `supabase_service_role`: Service role key de Supabase (para operaciones CRUD)
- `SYNOLOGY_IP`: IP del NAS Synology
- `SYNOLOGY_PORT`: Puerto del NAS (típicamente 5000)
- `SYNOLOGY_USER`: Usuario del NAS
- `SYNOLOGY_PASS`: Contraseña del NAS
- `SYNOLOGY_SHARED_FOLDER`: Carpeta compartida en el NAS

### Configuración WordPress (config.ini)
- `[wordpress].url`: URL base del sitio WordPress.com

## 📝 Uso

```bash
# Ejecutar el extractor principal
python src/main.py

# Ejecutar en modo dry-run (solo mostrar datos sin guardar)
python src/main.py --dry-run
```

El extractor:
1. **Lee episodios** desde la API de WordPress.com
2. **Extrae playlists** de canciones del contenido HTML
3. **Descarga MP3** y extrae duración exacta
4. **Sube archivos** al NAS Synology
5. **Guarda datos** en Supabase (podcasts + canciones)

## 🛠️ Desarrollo

El proyecto está diseñado para ser modular y extensible:

- **Componentes**: Cada funcionalidad está en su propio módulo
- **Configuración**: Centralizada en `config.ini` y variables de entorno
- **Logging**: Sistema de logs integrado para debugging
- **Base de datos**: Integración con Supabase para persistencia
- **RLS**: Row Level Security configurado para operaciones seguras

## 🔒 Seguridad

- **Row Level Security (RLS)**: Configurado en Supabase para ambas tablas
- **Service Role Key**: Usada para operaciones CRUD desde el backend
- **Credenciales**: Almacenadas en variables de entorno seguras

## 📄 Licencia

Este proyecto es parte del sistema de extracción de Popcasting. 
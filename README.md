# Extractor de WordPress para Popcasting

Extractor independiente para procesar episodios de Popcasting desde la API de WordPress.com, con integración a Supabase y almacenamiento en NAS Synology.

## 🎙️ RSS Feed Generado

Este proyecto también incluye un **feed RSS generado automáticamente** desde Supabase:

- **URL**: `https://ndhmlymnbrewflharfmr.supabase.co/functions/v1/rss`
- **Episodios**: 486 (todos los episodios)
- **Formato**: RSS 2.0 + iTunes completo
- **Plataformas**: iTunes, Spotify, Google Podcasts

📖 **Documentación RSS**: [`docs/05-RSS_FEED_SETUP.md`](docs/05-RSS_FEED_SETUP.md)

### ⚡ Quick Start RSS
```bash
# Desplegar RSS
./deploy_rss.sh

# Probar Feed
curl https://ndhmlymnbrewflharfmr.supabase.co/functions/v1/rss
```

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
├── scripts/                      # Scripts de utilidad
│   └── backup_supabase.py        # Script de backup
├── supabase/                     # Edge Functions
│   └── functions/
│       └── rss/                  # Función RSS
└── src/
    ├── components/               # Componentes principales
    │   ├── config_manager.py     # Gestor de configuración
    │   ├── database_manager.py   # Gestor de base de datos
    │   ├── song_processor.py     # Procesador de canciones
    │   ├── mp3_manager.py        # Gestor de archivos MP3 (descarga + duración)
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
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar en modo dry-run
python src/main.py --dry-run
```

## 📚 Documentación

### 📖 Guías Principales
- **📋 Índice**: [`docs/00-README.md`](docs/00-README.md)
- **🚀 Instalación**: [`docs/01-INSTALACION.md`](docs/01-INSTALACION.md)
- **🏗️ Arquitectura**: [`docs/02-ARQUITECTURA.md`](docs/02-ARQUITECTURA.md)
- **📝 TODOs**: [`docs/03-TODOs.md`](docs/03-TODOs.md)

### 🔄 Migración y Evolución
- **🔄 Migración**: [`docs/04-MIGRACION_RSS_A_WORDPRESS.md`](docs/04-MIGRACION_RSS_A_WORDPRESS.md)

### 🚀 Funcionalidades
- **📡 RSS Setup**: [`docs/05-RSS_FEED_SETUP.md`](docs/05-RSS_FEED_SETUP.md)

### 🎵 Componentes de Audio
- **🎵 MP3Manager**: [`docs/06-MP3_MANAGER.md`](docs/06-MP3_MANAGER.md) *(Documentación completa con mejoras y guías)*

### 🗄️ Synology NAS
- **🗄️ SynologyClient**: [`docs/07-SYNOLOGY_CLIENT.md`](docs/07-SYNOLOGY_CLIENT.md) *(Documentación completa)*

## 🔧 Configuración Post-Despliegue RSS

**IMPORTANTE**: Después de cada `./deploy_rss.sh`:

1. Ve a: https://supabase.com/dashboard/project/ndhmlymnbrewflharfmr/functions
2. Haz clic en `rss`
3. Settings → Desactiva "Verify JWT with legacy secret"
4. Save

## 📊 Estado Actual

- ✅ **Episodios procesados**: 486
- ✅ **Canciones extraídas**: 12,000+
- ✅ **Archivos MP3**: Descargados y subidos al NAS
- ✅ **Feed RSS**: Generado automáticamente
- ✅ **RLS**: Configurado en Supabase

## 🔒 Seguridad

- **Row Level Security (RLS)** configurado en Supabase
- **Service Role Key** para operaciones privilegiadas
- **Variables de entorno** para credenciales sensibles
- **Validación de datos** antes de inserción

---

**Última actualización**: Enero 2025 
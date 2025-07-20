# 🎵 Popcasting Extractor

Extractor completo de episodios del podcast Popcasting con base de datos Supabase.

## 📊 **Estado del Proyecto**

### ✅ **Base de Datos Supabase**
- **Total episodios**: 486
- **Cobertura**: 100% (486/486 episodios)
- **Estado**: Completa y sincronizada

### 🏆 **Logros Recientes**
- ✅ **100% de cobertura** alcanzado en Supabase
- ✅ **11 episodios faltantes** extraídos y actualizados
- ✅ **Migración a Supabase** como única base de datos
- ✅ **Proyecto reorganizado** y optimizado

## 🚀 **Uso Rápido**

### 📋 **Requisitos**
```bash
# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 🎯 **Ejecutar Extractor Principal**
```bash
python main.py
```

### 📊 **Generar Informe de Estado**
```bash
python generar_informe.py
```

## 📁 **Estructura del Proyecto**

```
popcasting_extractor/
├── README.md                 # Este archivo
├── main.py                   # Script principal
├── generar_informe.py        # Generador de informes
├── pyproject.toml           # Configuración del proyecto
├── services/                # Servicios principales
│   ├── popcasting_extractor.py
│   ├── supabase_database.py
│   └── config.py
├── scripts/                 # Scripts organizados
│   ├── extraction/          # Scripts de extracción
│   ├── reports/             # Generadores de informes
│   └── utils/               # Utilidades
├── docs/                    # Documentación
│   ├── episodes/            # Documentación de episodios
│   ├── migration/           # Documentación de migración
│   └── technical/           # Documentación técnica
├── data/                    # Archivos de datos
├── logs/                    # Logs del sistema
├── outputs/                 # Salidas del sistema
├── migration/               # Scripts de migración
└── test/                    # Tests
```

## 🔧 **Configuración**

### 📊 **Base de Datos**
- **Principal**: Supabase (PostgreSQL)
- **Configuración**: `services/config.py`
- **Estado**: Única fuente de verdad

### 🛠️ **Scripts Disponibles**

#### 📥 **Extracción**
- `scripts/extraction/` - Scripts para extraer episodios específicos
- `scripts/extraction/extractor_episodios_antiguos.py` - Extractor general
- `scripts/extraction/actualizar_episodio_*.py` - Actualizaciones específicas

#### 📊 **Reportes**
- `generar_informe.py` - Informe de estado (script principal)
- `scripts/reports/batch_web_extraction.py` - Extracción web en lote
- `scripts/reports/verificar_episodios_faltantes.py` - Verificación

#### 🔧 **Utilidades**
- `scripts/utils/web_extractor.py` - Extractor web
- `scripts/utils/web_report.py` - Generador de reportes web

## 📈 **Estadísticas**

### 🎵 **Episodios por Año**
- **2008**: Episodios #0-91 (episodios antiguos)
- **2009-2024**: Episodios #92-485 (episodios regulares)
- **2025**: Episodios #486+ (episodios actuales)

### 📊 **Información Disponible**
- ✅ **Datos básicos**: Título, fecha, número de programa
- ✅ **URLs**: RSS feed, descarga, WordPress
- ✅ **Playlists**: Canciones completas de cada episodio
- ✅ **Enlaces extra**: Links adicionales y recursos
- ✅ **Imágenes**: Portadas de episodios
- ✅ **Metadatos**: Tamaño de archivo, duración, etc.

## 🔄 **Proceso de Extracción**

### 1. **Extracción RSS**
- Obtiene episodios del feed RSS de Popcasting
- Procesa metadatos básicos (título, fecha, URL)

### 2. **Extracción Web**
- Extrae información detallada de las páginas web
- Obtiene playlists, enlaces extra, imágenes

### 3. **Almacenamiento Supabase**
- Guarda toda la información en Supabase
- Mantiene consistencia y integridad de datos

## 🎉 **Beneficios**

### ✅ **Ventajas**
- **Una sola fuente de verdad**: No hay inconsistencias
- **Escalabilidad**: Supabase maneja grandes volúmenes
- **Colaboración**: Múltiples desarrolladores pueden acceder
- **Backup automático**: Supabase gestiona backups
- **API REST**: Acceso programático a los datos
- **Panel de administración**: Interfaz web para gestionar

### 🚀 **Rendimiento**
- **Consultas rápidas**: PostgreSQL optimizado
- **Índices automáticos**: Búsquedas eficientes
- **Conexiones pool**: Gestión eficiente

## 📝 **Documentación**

### 📚 **Documentos Disponibles**
- `docs/episodes/` - Documentación de episodios y extracciones
- `docs/migration/` - Documentación de migración a Supabase
- `docs/technical/` - Documentación técnica y TODOs

### 🔧 **Configuración**
- El proyecto usa Supabase por defecto
- Configuración en `services/config.py`
- Variables de entorno para credenciales

## 🗂️ **Organización del Proyecto**

### ✅ **Archivos Principales**
- `main.py` - Script principal del extractor
- `generar_informe.py` - Generador de informes de estado
- `services/` - Servicios principales del sistema

### 📁 **Scripts Organizados**
- `scripts/extraction/` - Scripts de extracción de episodios
- `scripts/reports/` - Generadores de informes y reportes
- `scripts/utils/` - Utilidades y herramientas

### 📚 **Documentación Organizada**
- `docs/episodes/` - Documentación específica de episodios
- `docs/migration/` - Documentación de migración
- `docs/technical/` - Documentación técnica

### 📊 **Datos y Logs**
- `data/` - Archivos de datos y listas
- `logs/` - Logs del sistema
- `outputs/` - Salidas generadas

## 🤝 **Contribución**

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

**🎯 Estado del Proyecto: COMPLETO Y FUNCIONAL**
**📊 Cobertura: 100% (486/486 episodios)**
**🏆 Base de Datos: Supabase (PostgreSQL)**
**📁 Proyecto: Organizado y optimizado** 
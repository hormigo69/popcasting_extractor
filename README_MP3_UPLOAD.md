# Descarga y Subida de MP3 al NAS Synology

Este script descarga todos los MP3 de los episodios de Popcasting desde Supabase y los sube al NAS Synology.

## ✅ Estado Actual

- **Script principal**: `scripts/utils/download_and_upload_mp3.py` ✅
- **Conexión a Supabase**: 485 episodios con URLs de descarga ✅
- **Descarga de MP3**: Funcionando correctamente ✅
- **Cliente Synology**: Implementado y probado ✅
- **Scripts de prueba**: Creados y funcionando ✅

## ⚠️ Configuración Pendiente

**IMPORTANTE**: Las variables de entorno del NAS no están configuradas.

### Para configurar el NAS:

1. **Ejecutar el script de configuración**:
   ```bash
   uv run python setup_synology_env.py
   ```

2. **O crear manualmente el archivo `.env`** con:
   ```
   SYNOLOGY_IP=192.168.1.100
   SYNOLOGY_PORT=5000
   SYNOLOGY_USER=tu_usuario
   SYNOLOGY_PASS=tu_contraseña
   ```

## Uso

### 1. Configurar NAS (requerido)
```bash
uv run python setup_synology_env.py
```

### 2. Prueba de conexión a Supabase
```bash
uv run python test_mp3_script.py
```

### 3. Prueba de descarga de MP3
```bash
uv run python test_mp3_download.py
```

### 4. Prueba con 3 archivos (recomendado)
```bash
uv run python test_mp3_3_files_v2.py
```

### 5. Descarga y subida completa al NAS
```bash
uv run python scripts/utils/download_and_upload_mp3.py
```

## Funcionamiento

1. **Conecta a Supabase** y obtiene todos los episodios con URLs de descarga
2. **Descarga cada MP3** temporalmente al directorio `temp_mp3/`
3. **Sube al NAS** en la carpeta `/mp3/` con el formato `popcasting_XXXX.mp3`
4. **Limpia archivos temporales** después de cada subida
5. **Genera un log detallado** en `logs/mp3_upload_YYYYMMDD_HHMMSS.log`

## Resultado

- **485 episodios** con URLs de descarga disponibles
- **Archivos nombrados** como `popcasting_0000.mp3`, `popcasting_0001.mp3`, etc.
- **Log completo** con éxitos y errores
- **Limpieza automática** de archivos temporales

## Pruebas Realizadas

### ✅ Exitosas:
- Conexión a Supabase: 485 episodios encontrados
- Descarga de MP3: 109MB de prueba descargado correctamente
- Autenticación con NAS: Conexión establecida

### ⚠️ Pendientes:
- Subida al NAS: Requiere configuración de variables de entorno
- Error 408: Problema de permisos/configuración del NAS

## Notas

- El script procesa los episodios en orden por número
- Si un archivo ya existe en el NAS, se sobrescribe
- Los errores de descarga o subida se registran en el log
- El proceso puede tardar varias horas dependiendo del tamaño de los archivos
- **Recomendación**: Probar primero con 3 archivos antes de ejecutar el proceso completo 
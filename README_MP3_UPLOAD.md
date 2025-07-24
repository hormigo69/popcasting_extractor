# Descarga y Subida de MP3 al NAS Synology

Este script descarga todos los MP3 de los episodios de Popcasting desde Supabase y los sube al NAS Synology.

## Requisitos

1. **Configuración de Supabase**: Las variables de entorno deben estar configuradas en `.env`:
   ```
   supabase_project_url=tu_url_de_supabase
   supabase_api_key=tu_api_key_de_supabase
   ```

2. **Configuración del NAS Synology**: Crear archivo `.env` con las credenciales del NAS:
   ```
   SYNOLOGY_IP=192.168.1.100
   SYNOLOGY_PORT=5000
   SYNOLOGY_USER=tu_usuario
   SYNOLOGY_PASS=tu_contraseña
   ```

## Uso

### Prueba de conexión a Supabase
```bash
uv run python test_mp3_script.py
```

### Prueba de descarga de MP3
```bash
uv run python test_mp3_download.py
```

### Descarga y subida completa al NAS
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

## Notas

- El script procesa los episodios en orden por número
- Si un archivo ya existe en el NAS, se sobrescribe
- Los errores de descarga o subida se registran en el log
- El proceso puede tardar varias horas dependiendo del tamaño de los archivos 
# Análisis del RSS de Popcasting

## URL del RSS
https://feeds.feedburner.com/Popcasting

## Estructura identificada

### Información del canal
- Título: Popcasting
- Enlace: https://www.ivoox.com/podcast-popcasting_sq_f1590_1.html
- Descripción: Selección quincenal de la mejor nueva música independiente y mainstream
- Idioma: es (español)

### Estructura de cada episodio (item)
1. **Título**: Formato "PopcastingXXX" (ej: Popcasting483)
2. **Enlace web**: URL de iVoox con formato https://www.ivoox.com/popcastingXXX-audios-mp3_rf_XXXXXXX_1.html
3. **URL de descarga**: En el tag `enclosure` con formato https://www.ivoox.com/popcastingXXX_mf_XXXXXXX_feed_1.mp3
4. **Descripción/Playlist**: Contiene las canciones en formato "artista · canción :: artista · canción :: ..."
5. **Fecha de publicación**: En formato RFC 2822
6. **Duración**: En formato HH:MM:SS
7. **GUID**: URL única del episodio

### Formato de las canciones
- Separador entre artista y canción: " · "
- Separador entre canciones: " :: "
- Al final aparece información extra como enlaces (ej: "invita a Popcasting a café https://ko-fi.com/popcasting")

### Ejemplo del episodio 483:
- Número: 483
- URL web: https://www.ivoox.com/popcasting483-audios-mp3_rf_152795387_1.html
- URL descarga: https://www.ivoox.com/popcasting483_mf_152795387_feed_1.mp3?d=1752393173
- Primera canción: "boyd bennett · seventeen"
- Segunda canción: "don julian & the meadowlarks · boogie woogie"


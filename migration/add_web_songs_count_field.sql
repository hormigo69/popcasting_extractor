-- Script para añadir el campo web_songs_count a la tabla podcasts
-- Ejecutar este script en el SQL Editor de Supabase

-- Añadir el campo web_songs_count a la tabla podcasts
ALTER TABLE podcasts ADD COLUMN IF NOT EXISTS web_songs_count INTEGER;

-- Crear un índice para mejorar el rendimiento de consultas por número de canciones
CREATE INDEX IF NOT EXISTS idx_podcasts_web_songs_count ON podcasts(web_songs_count);

-- Comentario sobre el campo
COMMENT ON COLUMN podcasts.web_songs_count IS 'Número de canciones extraído de web_playlist'; 
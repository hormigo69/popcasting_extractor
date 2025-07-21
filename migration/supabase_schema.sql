-- Script SQL para crear las tablas en Supabase
-- Ejecutar este script en el SQL Editor de Supabase

-- Crear tabla de podcasts
CREATE TABLE IF NOT EXISTS podcasts (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    date DATE NOT NULL UNIQUE,
    url TEXT,
    download_url TEXT,
    file_size INTEGER,
    program_number INTEGER,
    wordpress_url TEXT,
    cover_image_url TEXT,
    web_extra_links TEXT,
    web_playlist TEXT,
    web_songs_count INTEGER,
    last_web_check TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear tabla de canciones
CREATE TABLE IF NOT EXISTS songs (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    position INTEGER,
    podcast_id BIGINT REFERENCES podcasts(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear tabla de links extras
CREATE TABLE IF NOT EXISTS extra_links (
    id BIGSERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    url TEXT NOT NULL,
    podcast_id BIGINT REFERENCES podcasts(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_podcasts_date ON podcasts(date);
CREATE INDEX IF NOT EXISTS idx_podcasts_program_number ON podcasts(program_number);
CREATE INDEX IF NOT EXISTS idx_songs_podcast_id ON songs(podcast_id);
CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(artist);
CREATE INDEX IF NOT EXISTS idx_songs_title ON songs(title);
CREATE INDEX IF NOT EXISTS idx_extra_links_podcast_id ON extra_links(podcast_id);

-- Crear función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Crear trigger para actualizar updated_at en podcasts
CREATE TRIGGER update_podcasts_updated_at 
    BEFORE UPDATE ON podcasts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Habilitar Row Level Security (RLS) - opcional
-- ALTER TABLE podcasts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE songs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE extra_links ENABLE ROW LEVEL SECURITY;

-- Crear políticas RLS básicas (descomentar si se habilita RLS)
-- CREATE POLICY "Allow all operations for authenticated users" ON podcasts FOR ALL USING (auth.role() = 'authenticated');
-- CREATE POLICY "Allow all operations for authenticated users" ON songs FOR ALL USING (auth.role() = 'authenticated');
-- CREATE POLICY "Allow all operations for authenticated users" ON extra_links FOR ALL USING (auth.role() = 'authenticated'); 
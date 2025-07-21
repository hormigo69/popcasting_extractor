-- Script SQL para optimizar los tipos de campo en Supabase
-- Ejecutar este script en el SQL Editor de Supabase

-- Optimizar tipos de campo en la tabla podcasts
-- Convertir program_number de TEXT a INTEGER
-- Convertir date de TEXT a DATE

-- Primero, verificar que los datos sean válidos antes de cambiar tipos
-- Esto evitará errores durante la conversión

-- Verificar program_number
SELECT 
    COUNT(*) as total_records,
    COUNT(CASE WHEN program_number ~ '^[0-9]+$' THEN 1 END) as valid_numbers,
    COUNT(CASE WHEN program_number !~ '^[0-9]+$' THEN 1 END) as invalid_numbers
FROM podcasts;

-- Verificar date
SELECT 
    COUNT(*) as total_records,
    COUNT(CASE WHEN date ~ '^\d{4}-\d{2}-\d{2}$' THEN 1 END) as valid_dates,
    COUNT(CASE WHEN date !~ '^\d{4}-\d{2}-\d{2}$' THEN 1 END) as invalid_dates
FROM podcasts;

-- Limpiar program_number: convertir a entero y limpiar caracteres no numéricos
UPDATE podcasts 
SET program_number = REGEXP_REPLACE(program_number, '[^0-9]', '', 'g')
WHERE program_number IS NOT NULL;

-- Limpiar date: asegurar formato YYYY-MM-DD
UPDATE podcasts 
SET date = TO_CHAR(TO_DATE(date, 'YYYY-MM-DD'), 'YYYY-MM-DD')
WHERE date IS NOT NULL 
  AND date ~ '^\d{4}-\d{2}-\d{2}$';

-- Ahora cambiar los tipos de columna
-- Nota: Esto puede fallar si hay datos inválidos
ALTER TABLE podcasts 
ALTER COLUMN program_number TYPE INTEGER USING program_number::INTEGER,
ALTER COLUMN date TYPE DATE USING date::DATE;

-- Recrear índices para optimizar consultas
DROP INDEX IF EXISTS idx_podcasts_date;
DROP INDEX IF EXISTS idx_podcasts_program_number;

CREATE INDEX idx_podcasts_date ON podcasts(date);
CREATE INDEX idx_podcasts_program_number ON podcasts(program_number);

-- Verificar que la conversión fue exitosa
SELECT 
    'program_number' as column_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN program_number IS NOT NULL THEN 1 END) as non_null_values,
    MIN(program_number) as min_value,
    MAX(program_number) as max_value
FROM podcasts
UNION ALL
SELECT 
    'date' as column_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN date IS NOT NULL THEN 1 END) as non_null_values,
    MIN(date) as min_value,
    MAX(date) as max_value
FROM podcasts;

-- Mostrar algunos ejemplos de datos convertidos
SELECT 
    id,
    title,
    date,
    program_number,
    url
FROM podcasts 
ORDER BY program_number 
LIMIT 10; 
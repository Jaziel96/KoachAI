-- US-003: Tabla para almacenar los planes generados por Claude
-- Ejecutar en la consola SQL de Supabase

CREATE TABLE IF NOT EXISTS planes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    contenido TEXT NOT NULL,
    tmb DECIMAL(7,2),
    tdee DECIMAL(7,2),
    meta_calorica DECIMAL(7,2),
    generado_en DECIMAL(5,2),
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

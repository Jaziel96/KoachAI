-- US-002: Tablas para usuarios y flujo de onboarding
-- Ejecutar en la consola SQL de Supabase

CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS perfiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    edad INTEGER NOT NULL,
    peso_kg DECIMAL(5,2) NOT NULL,
    talla_cm INTEGER NOT NULL,
    genero TEXT NOT NULL,
    meta TEXT NOT NULL,
    alergias TEXT DEFAULT 'ninguna',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS consentimientos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    acepto BOOLEAN NOT NULL,
    fecha TIMESTAMPTZ DEFAULT NOW(),
    version_aviso TEXT DEFAULT '1.0'
);

CREATE TABLE IF NOT EXISTS onboarding_estado (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number TEXT UNIQUE NOT NULL,
    paso_actual INTEGER DEFAULT 0,
    datos_parciales JSONB DEFAULT '{}',
    intentos_paso INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- US-013: lista de espera de la landing.
-- BORRADOR para integrar en las migraciones de Alembic (backend/migrations/):
-- el esquema de `leads_iniciales` no está definido en docs/ (solo su nombre en US-013),
-- así que estas columnas son una propuesta pendiente de aprobación.

create table if not exists public.leads_iniciales (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  nombre text not null,
  meta_principal text not null
    check (meta_principal in ('bajar_peso', 'ganar_musculo', 'comer_mejor', 'mas_energia', 'otra')),
  consentimiento_at timestamptz not null,
  fuente text not null default 'landing',
  created_at timestamptz not null default now(),
  -- La API guarda el email en minúsculas; el índice evita duplicados (CA-2).
  constraint leads_iniciales_email_key unique (email),
  constraint leads_iniciales_email_lower check (email = lower(email))
);

-- RLS (ADR-006): sin políticas, anon y authenticated no pueden leer ni escribir.
-- Solo la service_key (servidor de la landing) accede, y esta se salta RLS.
alter table public.leads_iniciales enable row level security;

-- ==============================
-- 1. EXTENSÕES
-- ==============================
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==============================
-- 2. ENUM DE PAPÉIS
-- ==============================
DO $$ BEGIN
  CREATE TYPE user_role AS ENUM (
    'ADMIN_MASTER',
    'IMOBILIARIA',
    'CORRETOR',
    'CLIENTE'
  );
EXCEPTION
  WHEN duplicate_object THEN null;
END $$;

-- ==============================
-- 3. TABELA USERS
-- ==============================
CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  role user_role NOT NULL,
  imobiliaria_id uuid NULL,
  criado_em timestamp DEFAULT now()
);

-- ==============================
-- 4. TABELA IMOBILIARIAS
-- ==============================
CREATE TABLE IF NOT EXISTS imobiliarias (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  nome text NOT NULL,
  email text UNIQUE NOT NULL,
  criado_por uuid REFERENCES users(id),
  criado_em timestamp DEFAULT now()
);

-- ==============================
-- 5. TABELA CORRETORES
-- ==============================
CREATE TABLE IF NOT EXISTS corretores (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id),
  nome text,
  email text,
  imobiliaria_id uuid NULL REFERENCES imobiliarias(id),
  criado_por uuid REFERENCES users(id),
  criado_em timestamp DEFAULT now()
);

-- ==============================
-- 6. ATIVAR RLS
-- ==============================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE imobiliarias ENABLE ROW LEVEL SECURITY;
ALTER TABLE corretores ENABLE ROW LEVEL SECURITY;

-- ==============================
-- 7. POLÍTICAS USERS
-- ==============================
DROP POLICY IF EXISTS "Admin acessa tudo users" ON users;
CREATE POLICY "Admin acessa tudo users"
ON users
FOR ALL
USING (auth.jwt() ->> 'role' = 'ADMIN_MASTER');

DROP POLICY IF EXISTS "User vê próprio perfil" ON users;
CREATE POLICY "User vê próprio perfil"
ON users
FOR SELECT
USING (auth.uid() = id);

-- ==============================
-- 8. POLÍTICAS IMOBILIARIAS
-- ==============================
DROP POLICY IF EXISTS "Admin controla imobiliarias" ON imobiliarias;
CREATE POLICY "Admin controla imobiliarias"
ON imobiliarias
FOR ALL
USING (auth.jwt() ->> 'role' = 'ADMIN_MASTER');

DROP POLICY IF EXISTS "Imobiliaria vê seu registro" ON imobiliarias;
CREATE POLICY "Imobiliaria vê seu registro"
ON imobiliarias
FOR SELECT
USING (
  auth.jwt() ->> 'role' = 'IMOBILIARIA'
  AND id = (auth.jwt() ->> 'imobiliaria_id')::uuid
);

-- ==============================
-- 9. POLÍTICAS CORRETORES
-- ==============================

-- Admin vê apenas os que ele criou
DROP POLICY IF EXISTS "Admin vê seus corretores" ON corretores;
CREATE POLICY "Admin vê seus corretores"
ON corretores
FOR SELECT
USING (
  auth.jwt() ->> 'role' = 'ADMIN_MASTER'
  AND criado_por = auth.uid()
);

-- Imobiliária gerencia seus corretores
DROP POLICY IF EXISTS "Imobiliaria gerencia corretores" ON corretores;
CREATE POLICY "Imobiliaria gerencia corretores"
ON corretores
FOR ALL
USING (
  auth.jwt() ->> 'role' = 'IMOBILIARIA'
  AND imobiliaria_id = (auth.jwt() ->> 'imobiliaria_id')::uuid
);

-- Corretor vê apenas seu registro
DROP POLICY IF EXISTS "Corretor vê próprio registro" ON corretores;
CREATE POLICY "Corretor vê próprio registro"
ON corretores
FOR SELECT
USING (
  auth.jwt() ->> 'role' = 'CORRETOR'
  AND user_id = auth.uid()
);

-- ==============================
-- 10. TRIGGER
-- ==============================
CREATE OR REPLACE FUNCTION set_corretor_defaults()
RETURNS trigger AS $$
BEGIN

  IF (auth.jwt() ->> 'role') = 'IMOBILIARIA' THEN
    NEW.imobiliaria_id := (auth.jwt() ->> 'imobiliaria_id')::uuid;
    NEW.criado_por := auth.uid();
  END IF;

  IF (auth.jwt() ->> 'role') = 'ADMIN_MASTER' THEN
    NEW.imobiliaria_id := NULL;
    NEW.criado_por := auth.uid();
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_set_corretor_defaults ON corretores;
CREATE TRIGGER trigger_set_corretor_defaults
BEFORE INSERT ON corretores
FOR EACH ROW
EXECUTE FUNCTION set_corretor_defaults();

-- ==============================
-- 11. DADOS INICIAIS
-- ==============================

-- ADMIN MASTER
INSERT INTO users (email, role)
VALUES ('admin@imovia.com', 'ADMIN_MASTER')
ON CONFLICT (email) DO NOTHING;

-- IMOBILIÁRIAS
INSERT INTO imobiliarias (nome, email)
VALUES 
('Alpha Imobiliária', 'alpha@imovia.com'),
('Beta Imobiliária', 'beta@imovia.com')
ON CONFLICT (email) DO NOTHING;

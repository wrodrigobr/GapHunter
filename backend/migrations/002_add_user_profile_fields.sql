-- Migração: Adicionar campos de perfil de poker aos usuários
-- Data: 2025-07-28
-- Descrição: Adiciona campos específicos de poker para personalização da experiência

-- Adicionar novos campos à tabela users
ALTER TABLE users 
ADD COLUMN full_name VARCHAR(100) DEFAULT '' NOT NULL,
ADD COLUMN poker_experience VARCHAR(20) DEFAULT NULL,
ADD COLUMN preferred_games VARCHAR(20) DEFAULT NULL,
ADD COLUMN main_stakes VARCHAR(20) DEFAULT NULL,
ADD COLUMN poker_goals VARCHAR(20) DEFAULT NULL,
ADD COLUMN country VARCHAR(50) DEFAULT NULL,
ADD COLUMN timezone VARCHAR(50) DEFAULT NULL;

-- Atualizar usuários existentes com valores padrão
UPDATE users 
SET full_name = COALESCE(username, 'Usuário') 
WHERE full_name = '' OR full_name IS NULL;

-- Adicionar comentários para documentação
COMMENT ON COLUMN users.full_name IS 'Nome completo do usuário';
COMMENT ON COLUMN users.poker_experience IS 'Nível de experiência: beginner, intermediate, advanced, professional';
COMMENT ON COLUMN users.preferred_games IS 'Tipo de jogo preferido: cash, tournaments, both';
COMMENT ON COLUMN users.main_stakes IS 'Stakes principais: micro, low, mid, high';
COMMENT ON COLUMN users.poker_goals IS 'Objetivos no poker: recreational, profit, professional';
COMMENT ON COLUMN users.country IS 'País do usuário';
COMMENT ON COLUMN users.timezone IS 'Fuso horário do usuário';

-- Criar índices para campos que podem ser usados em consultas
CREATE INDEX idx_users_poker_experience ON users(poker_experience);
CREATE INDEX idx_users_preferred_games ON users(preferred_games);
CREATE INDEX idx_users_country ON users(country);

-- Verificar se a migração foi aplicada corretamente
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
    AND column_name IN (
        'full_name', 
        'poker_experience', 
        'preferred_games', 
        'main_stakes', 
        'poker_goals', 
        'country', 
        'timezone'
    )
ORDER BY ordinal_position;


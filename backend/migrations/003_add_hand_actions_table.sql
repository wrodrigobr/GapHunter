-- Migração: Adicionar tabela hand_actions para armazenar ações das mãos
-- Data: 2025-01-15
-- Descrição: Cria tabela para armazenar ações individuais de cada mão com identificação da street

-- Criar tabela hand_actions
CREATE TABLE hand_actions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    hand_id INT NOT NULL,
    street VARCHAR(20) NOT NULL,  -- preflop, flop, turn, river
    player_name VARCHAR(50) NOT NULL,
    action_type VARCHAR(20) NOT NULL,  -- fold, check, call, bet, raise, all-in
    amount DECIMAL(10,2) DEFAULT 0.00,
    total_bet DECIMAL(10,2) DEFAULT 0.00,
    timestamp DATETIME2 DEFAULT GETDATE(),
    action_order INT NOT NULL,  -- Ordem da ação na street
    created_at DATETIME2 DEFAULT GETDATE(),
    
    -- Chaves estrangeiras
    CONSTRAINT FK_hand_actions_hand_id FOREIGN KEY (hand_id) REFERENCES hands(id) ON DELETE CASCADE
);

-- Adicionar comentários para documentação
EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Tabela para armazenar ações individuais de cada mão de poker', 
    @level0type = N'SCHEMA', @level0name = N'dbo', 
    @level1type = N'TABLE', @level1name = N'hand_actions';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'ID da mão na tabela hands', 
    @level0type = N'SCHEMA', @level0name = N'dbo', 
    @level1type = N'TABLE', @level1name = N'hand_actions', 
    @level2type = N'COLUMN', @level2name = N'hand_id';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Street da ação: preflop, flop, turn, river', 
    @level0type = N'SCHEMA', @level0name = N'dbo', 
    @level1type = N'TABLE', @level1name = N'hand_actions', 
    @level2type = N'COLUMN', @level2name = N'street';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Nome do jogador que fez a ação', 
    @level0type = N'SCHEMA', @level0name = N'dbo', 
    @level1type = N'TABLE', @level1name = N'hand_actions', 
    @level2type = N'COLUMN', @level2name = N'player_name';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Tipo da ação: fold, check, call, bet, raise, all-in', 
    @level0type = N'SCHEMA', @level0name = N'dbo', 
    @level1type = N'TABLE', @level1name = N'hand_actions', 
    @level2type = N'COLUMN', @level2name = N'action_type';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Valor da ação (para bet, call, raise)', 
    @level0type = N'SCHEMA', @level0name = N'dbo', 
    @level1type = N'TABLE', @level1name = N'hand_actions', 
    @level2type = N'COLUMN', @level2name = N'amount';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Aposta total do jogador após a ação', 
    @level0type = N'SCHEMA', @level0name = N'dbo', 
    @level1type = N'TABLE', @level1name = N'hand_actions', 
    @level2type = N'COLUMN', @level2name = N'total_bet';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Ordem da ação na street (para manter sequência)', 
    @level0type = N'SCHEMA', @level0name = N'dbo', 
    @level1type = N'TABLE', @level1name = N'hand_actions', 
    @level2type = N'COLUMN', @level2name = N'action_order';

-- Criar índices para performance
CREATE INDEX idx_hand_actions_hand_id ON hand_actions(hand_id);
CREATE INDEX idx_hand_actions_street ON hand_actions(street);
CREATE INDEX idx_hand_actions_player ON hand_actions(player_name);
CREATE INDEX idx_hand_actions_type ON hand_actions(action_type);
CREATE INDEX idx_hand_actions_order ON hand_actions(action_order);

-- Criar view para facilitar consultas de ações por mão
CREATE VIEW hand_actions_summary AS
SELECT 
    ha.hand_id,
    ha.street,
    COUNT(*) as total_actions,
    COUNT(CASE WHEN ha.action_type = 'fold' THEN 1 END) as folds,
    COUNT(CASE WHEN ha.action_type = 'check' THEN 1 END) as checks,
    COUNT(CASE WHEN ha.action_type = 'call' THEN 1 END) as calls,
    COUNT(CASE WHEN ha.action_type = 'bet' THEN 1 END) as bets,
    COUNT(CASE WHEN ha.action_type = 'raise' THEN 1 END) as raises,
    COUNT(CASE WHEN ha.action_type = 'all-in' THEN 1 END) as all_ins,
    SUM(ha.amount) as total_amount,
    -- Campo calculado para ordenação (não usado na view, mas disponível para consultas)
    CASE ha.street 
        WHEN 'preflop' THEN 1 
        WHEN 'flop' THEN 2 
        WHEN 'turn' THEN 3 
        WHEN 'river' THEN 4 
    END as street_order
FROM hand_actions ha
GROUP BY ha.hand_id, ha.street;

-- Verificar se a tabela foi criada corretamente
SELECT 
    TABLE_NAME, 
    COLUMN_NAME, 
    DATA_TYPE, 
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'hand_actions'
ORDER BY ORDINAL_POSITION;

-- Verificar se a view foi criada
SELECT 
    TABLE_NAME, 
    TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_NAME IN ('hand_actions', 'hand_actions_summary');

-- Verificar se os índices foram criados
SELECT 
    i.name AS index_name,
    t.name AS table_name,
    c.name AS column_name
FROM sys.indexes i
INNER JOIN sys.tables t ON i.object_id = t.object_id
INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE t.name = 'hand_actions'
ORDER BY i.name, ic.key_ordinal; 
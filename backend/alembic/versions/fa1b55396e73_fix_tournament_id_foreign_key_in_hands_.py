"""Fix tournament_id foreign key in hands table

Revision ID: fa1b55396e73
Revises: 681bfb86d9c7
Create Date: 2025-07-28 22:56:31.909376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa1b55396e73'
down_revision: Union[str, None] = '681bfb86d9c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Para SQLite: Recriar tabela com nova estrutura
    # Para SQL Server: Usar ALTER COLUMN
    
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    if dialect_name == 'sqlite':
        # SQLite: Recriar tabela
        print("🔧 SQLite detectado - recriando tabela hands")
        
        # Criar nova tabela temporária
        op.create_table('hands_new',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('tournament_id', sa.Integer(), nullable=True),  # Agora é Integer
            sa.Column('hand_id', sa.String(length=50), nullable=False),
            sa.Column('pokerstars_tournament_id', sa.String(length=50), nullable=True),
            sa.Column('table_name', sa.String(length=100), nullable=True),
            sa.Column('date_played', sa.DateTime(), nullable=True),
            sa.Column('hero_name', sa.String(length=50), nullable=True),
            sa.Column('hero_position', sa.String(length=10), nullable=True),
            sa.Column('hero_cards', sa.String(length=10), nullable=True),
            sa.Column('hero_action', sa.String(length=20), nullable=True),
            sa.Column('pot_size', sa.Float(), nullable=True),
            sa.Column('bet_amount', sa.Float(), nullable=True),
            sa.Column('board_cards', sa.String(length=20), nullable=True),
            sa.Column('raw_hand', sa.Text(), nullable=True),
            sa.Column('ai_analysis', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
            sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Copiar dados (tournament_id será NULL para valores grandes)
        op.execute("""
            INSERT INTO hands_new (
                id, user_id, tournament_id, hand_id, pokerstars_tournament_id,
                table_name, date_played, hero_name, hero_position, hero_cards,
                hero_action, pot_size, bet_amount, board_cards, raw_hand,
                ai_analysis, created_at
            )
            SELECT 
                id, user_id, NULL as tournament_id, hand_id, tournament_id as pokerstars_tournament_id,
                table_name, date_played, hero_name, hero_position, hero_cards,
                hero_action, pot_size, bet_amount, board_cards, raw_hand,
                ai_analysis, created_at
            FROM hands
        """)
        
        # Remover tabela antiga e renomear nova
        op.drop_table('hands')
        op.rename_table('hands_new', 'hands')
        
    else:
        # SQL Server: Usar ALTER COLUMN
        print("🔧 SQL Server detectado - alterando coluna")
        
        # Primeiro remover constraint se existir
        try:
            op.drop_constraint('FK_hands_tournament_id', 'hands', type_='foreignkey')
        except:
            pass
        
        # Alterar tipo da coluna
        op.alter_column('hands', 'tournament_id',
                   existing_type=sa.VARCHAR(length=50),
                   type_=sa.Integer(),
                   existing_nullable=True)
        
        # Recriar foreign key
        op.create_foreign_key('FK_hands_tournament_id', 'hands', 'tournaments', ['tournament_id'], ['id'])
    
    # Corrigir campo nickname em users (para ambos)
    try:
        op.alter_column('users', 'nickname',
                   existing_type=sa.VARCHAR(length=50),
                   nullable=True)
    except:
        # Se falhar, ignorar (campo pode não existir ainda)
        pass


def downgrade() -> None:
    # Reverter mudanças
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    if dialect_name == 'sqlite':
        # SQLite: Recriar tabela com estrutura antiga
        op.create_table('hands_old',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('tournament_id', sa.String(length=50), nullable=True),  # Volta para String
            sa.Column('hand_id', sa.String(length=50), nullable=False),
            sa.Column('pokerstars_tournament_id', sa.String(length=50), nullable=True),
            sa.Column('table_name', sa.String(length=100), nullable=True),
            sa.Column('date_played', sa.DateTime(), nullable=True),
            sa.Column('hero_name', sa.String(length=50), nullable=True),
            sa.Column('hero_position', sa.String(length=10), nullable=True),
            sa.Column('hero_cards', sa.String(length=10), nullable=True),
            sa.Column('hero_action', sa.String(length=20), nullable=True),
            sa.Column('pot_size', sa.Float(), nullable=True),
            sa.Column('bet_amount', sa.Float(), nullable=True),
            sa.Column('board_cards', sa.String(length=20), nullable=True),
            sa.Column('raw_hand', sa.Text(), nullable=True),
            sa.Column('ai_analysis', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Copiar dados de volta
        op.execute("""
            INSERT INTO hands_old (
                id, user_id, tournament_id, hand_id, pokerstars_tournament_id,
                table_name, date_played, hero_name, hero_position, hero_cards,
                hero_action, pot_size, bet_amount, board_cards, raw_hand,
                ai_analysis, created_at
            )
            SELECT 
                id, user_id, pokerstars_tournament_id as tournament_id, hand_id, pokerstars_tournament_id,
                table_name, date_played, hero_name, hero_position, hero_cards,
                hero_action, pot_size, bet_amount, board_cards, raw_hand,
                ai_analysis, created_at
            FROM hands
        """)
        
        op.drop_table('hands')
        op.rename_table('hands_old', 'hands')
        
    else:
        # SQL Server
        op.drop_constraint('FK_hands_tournament_id', 'hands', type_='foreignkey')
        op.alter_column('hands', 'tournament_id',
                   existing_type=sa.Integer(),
                   type_=sa.VARCHAR(length=50),
                   existing_nullable=True)

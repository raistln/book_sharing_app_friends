"""update books: remove book_type, add new fields, make author nullable

Revision ID: zz_update_books_fields
Revises: ff40704dc4af
Create Date: 2025-01-18 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'zz_update_books_fields'
down_revision = 'ef6ad3d88b86'
branch_labels = None
depends_on = None


def upgrade():
    # Hacer author nullable
    op.alter_column('books', 'author',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
    
    # Agregar nuevos campos
    op.add_column('books', sa.Column('publisher', sa.String(length=200), nullable=True))
    op.add_column('books', sa.Column('published_date', sa.String(length=50), nullable=True))
    op.add_column('books', sa.Column('page_count', sa.String(length=10), nullable=True))
    op.add_column('books', sa.Column('language', sa.String(length=10), nullable=True))
    
    # Crear el enum de condition si no existe
    op.execute("CREATE TYPE book_condition AS ENUM ('new', 'like_new', 'good', 'fair', 'poor')")
    
    # Agregar columna condition con valor por defecto 'good'
    op.add_column('books', sa.Column('condition', 
                                     sa.Enum('new', 'like_new', 'good', 'fair', 'poor', 
                                            name='book_condition'), 
                                     nullable=True, 
                                     server_default='good'))
    
    # Eliminar columna book_type si existe
    try:
        op.drop_column('books', 'book_type')
        # Eliminar el enum book_type
        op.execute('DROP TYPE IF EXISTS book_type')
    except:
        pass  # Si no existe, continuar


def downgrade():
    # Revertir cambios
    op.drop_column('books', 'condition')
    op.drop_column('books', 'language')
    op.drop_column('books', 'page_count')
    op.drop_column('books', 'published_date')
    op.drop_column('books', 'publisher')
    
    # Hacer author NOT NULL de nuevo
    op.alter_column('books', 'author',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
    
    # Recrear book_type
    op.execute("CREATE TYPE book_type AS ENUM ('novel', 'comic', 'manga', 'graphic_novel', 'short_story', 'poetry', 'essay', 'biography', 'autobiography', 'other')")
    op.add_column('books', sa.Column('book_type', 
                                     sa.Enum('novel', 'comic', 'manga', 'graphic_novel', 'short_story', 'poetry', 'essay', 'biography', 'autobiography', 'other',
                                            name='book_type'), 
                                     nullable=True))
    
    # Eliminar enum condition
    op.execute('DROP TYPE IF EXISTS book_condition')

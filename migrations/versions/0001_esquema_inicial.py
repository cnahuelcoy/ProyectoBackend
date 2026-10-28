"""esquema inicial

Revision ID: 0001
Revises: 
Create Date: 2026-10-28 22:53:30.439839

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# identificadores de la revisión, usados por Alembic
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crea las tablas clientes, vehiculos, ordenes_trabajo y reparaciones."""
    op.create_table('clientes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nombre', sa.String(length=50), nullable=False),
    sa.Column('apellido', sa.String(length=50), nullable=False),
    sa.Column('telefono', sa.String(length=15), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('direccion', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('vehiculos',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('patente', sa.String(length=6), nullable=False),
    sa.Column('marca', sa.String(), nullable=False),
    sa.Column('modelo', sa.String(), nullable=False),
    sa.Column('anio', sa.Integer(), nullable=False),
    sa.Column('kilometraje', sa.Integer(), nullable=False),
    sa.Column('cliente_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('patente'),
    sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], )
    )
    op.create_table('ordenes_trabajo',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('vehiculo_id', sa.Integer(), nullable=False),
    sa.Column('fecha_ingreso', sa.Date(), nullable=False),
    sa.Column('descripcion_problema', sa.Text(), nullable=False),
    sa.Column('kilometraje_ingreso', sa.Integer(), nullable=False),
    sa.Column('estado', sa.Enum('pendiente', 'en_reparacion', 'finalizada', name='estado_orden_trabajo', native_enum=False, create_constraint=True), nullable=False),
    sa.ForeignKeyConstraint(['vehiculo_id'], ['vehiculos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reparaciones',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('orden_trabajo_id', sa.Integer(), nullable=False),
    sa.Column('descripcion', sa.Text(), nullable=False),
    sa.Column('tipo', sa.Enum('reparacion', 'mantencion', 'diagnostico', name='tipo_reparacion', native_enum=False, create_constraint=True), nullable=False),
    sa.Column('costo', sa.Float(), nullable=False),
    sa.Column('fecha', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['orden_trabajo_id'], ['ordenes_trabajo.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Elimina las tablas en orden inverso por las claves foráneas."""
    op.drop_table('reparaciones')
    op.drop_table('ordenes_trabajo')
    op.drop_table('vehiculos')
    op.drop_table('clientes')
"""Added quiz attempts

Revision ID: 2ca52ed61e3c
Revises: 8589684ad9c0
Create Date: 2025-03-30 12:14:15.900856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ca52ed61e3c'
down_revision = '8589684ad9c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('quiz_attempt',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('quiz_id', sa.Integer(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.Column('attempt_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['quiz_id'], ['quiz.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('quiz', schema=None) as batch_op:
        batch_op.alter_column('chapter_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quiz', schema=None) as batch_op:
        batch_op.alter_column('chapter_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    op.drop_table('quiz_attempt')
    # ### end Alembic commands ###

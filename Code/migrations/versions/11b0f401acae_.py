"""empty message

Revision ID: 11b0f401acae
Revises: be2599bce44e
Create Date: 2021-01-16 11:44:03.261130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11b0f401acae'
down_revision = 'be2599bce44e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('home_page_actions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('started_at', sa.DateTime(), nullable=False),
    sa.Column('sequence_number', sa.Integer(), nullable=False),
    sa.Column('bot_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['bot_id'], ['bots.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('home_page_results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('page_section', sa.String(), nullable=True),
    sa.Column('home_page_action_id', sa.Integer(), nullable=False),
    sa.Column('video_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['home_page_action_id'], ['home_page_actions.id'], ),
    sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('home_page_results')
    op.drop_table('home_page_actions')
    # ### end Alembic commands ###
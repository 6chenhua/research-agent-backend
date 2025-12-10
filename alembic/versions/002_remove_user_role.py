"""remove user_role field

Revision ID: 002
Revises: 001
Create Date: 2025-12-10 10:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """移除user_role字段和相关索引（v1.3要求）"""
    
    # 1. 删除user_role索引
    op.drop_index('idx_user_role', table_name='users')
    
    # 2. 删除user_role列
    op.drop_column('users', 'user_role')


def downgrade() -> None:
    """恢复user_role字段（回滚用）"""
    
    # 1. 添加user_role列
    op.add_column('users', 
        sa.Column('user_role', 
                  sa.Enum('student', 'researcher', 'teacher', name='userrole'), 
                  nullable=False, 
                  server_default='student', 
                  comment='用户角色')
    )
    
    # 2. 创建索引
    op.create_index('idx_user_role', 'users', ['user_role'])


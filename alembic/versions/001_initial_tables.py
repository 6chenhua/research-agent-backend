"""create initial tables

Revision ID: 001
Revises: 
Create Date: 2025-12-09 10:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建所有初始表"""
    
    # 1. 创建users表
    op.create_table(
        'users',
        sa.Column('user_id', sa.String(50), nullable=False, comment='用户ID'),
        sa.Column('username', sa.String(100), nullable=False, comment='用户名'),
        sa.Column('email', sa.String(100), nullable=False, comment='邮箱'),
        sa.Column('password_hash', sa.String(255), nullable=False, comment='密码哈希'),
        sa.Column('user_role', sa.Enum('student', 'researcher', 'teacher', name='userrole'), 
                  nullable=False, server_default='student', comment='用户角色'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1', comment='是否激活'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='0', comment='邮箱是否验证'),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0', comment='登录失败次数'),
        sa.Column('locked_until', mysql.TIMESTAMP(), nullable=True, comment='账户锁定到期时间'),
        sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), 
                  nullable=False, comment='创建时间'),
        sa.Column('last_login', mysql.TIMESTAMP(), nullable=True, comment='最后登录时间'),
        sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), 
                  nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('user_id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # 创建users表索引
    op.create_index('idx_email', 'users', ['email'], unique=True)
    op.create_index('idx_created_at', 'users', ['created_at'])
    op.create_index('idx_user_role', 'users', ['user_role'])
    
    # 2. 创建user_profiles表
    op.create_table(
        'user_profiles',
        sa.Column('user_id', sa.String(50), nullable=False, comment='用户ID'),
        sa.Column('research_direction', sa.Text(), nullable=True, comment='研究方向'),
        sa.Column('interests', mysql.JSON(), nullable=True, comment='兴趣标签'),
        sa.Column('expertise_level', sa.Enum('beginner', 'intermediate', 'advanced', 'expert', name='expertiselevel'),
                  nullable=True, server_default='beginner', comment='专业水平'),
        sa.Column('reading_count', sa.Integer(), nullable=False, server_default='0', comment='阅读论文数量'),
        sa.Column('chat_count', sa.Integer(), nullable=False, server_default='0', comment='聊天次数'),
        sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), 
                  nullable=False, comment='创建时间'),
        sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), 
                  nullable=False, comment='更新时间'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # 3. 创建chat_history表
    op.create_table(
        'chat_history',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('user_id', sa.String(50), nullable=False, comment='用户ID'),
        sa.Column('session_id', sa.String(100), nullable=True, comment='会话ID'),
        sa.Column('message', sa.Text(), nullable=False, comment='用户消息'),
        sa.Column('response', sa.Text(), nullable=False, comment='AI回复'),
        sa.Column('tools_used', mysql.JSON(), nullable=True, comment='使用的工具列表'),
        sa.Column('citations', mysql.JSON(), nullable=True, comment='引用来源'),
        sa.Column('confidence', sa.Integer(), nullable=True, comment='置信度'),
        sa.Column('timestamp', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), 
                  nullable=False, comment='时间戳'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # 创建chat_history表索引
    op.create_index('idx_user_time', 'chat_history', ['user_id', 'timestamp'])
    op.create_index('idx_session', 'chat_history', ['session_id'])
    
    # 4. 创建reading_history表
    op.create_table(
        'reading_history',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('user_id', sa.String(50), nullable=False, comment='用户ID'),
        sa.Column('paper_id', sa.String(100), nullable=False, comment='论文ID'),
        sa.Column('duration_seconds', sa.Integer(), nullable=False, server_default='0', comment='阅读时长'),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='0', comment='是否读完'),
        sa.Column('rating', sa.Integer(), nullable=True, comment='评分'),
        sa.Column('notes', sa.Text(), nullable=True, comment='笔记'),
        sa.Column('read_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), 
                  nullable=False, comment='阅读时间'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # 创建reading_history表索引
    op.create_index('idx_user_read', 'reading_history', ['user_id', 'read_at'])
    op.create_index('idx_paper', 'reading_history', ['paper_id'])
    op.create_index('idx_user_paper', 'reading_history', ['user_id', 'paper_id'])
    
    # 5. 创建paper_metadata表
    op.create_table(
        'paper_metadata',
        sa.Column('paper_id', sa.String(100), nullable=False, comment='论文ID'),
        sa.Column('title', sa.String(500), nullable=False, comment='论文标题'),
        sa.Column('authors', mysql.JSON(), nullable=True, comment='作者列表'),
        sa.Column('abstract', sa.Text(), nullable=True, comment='摘要'),
        sa.Column('year', sa.Integer(), nullable=True, comment='发表年份'),
        sa.Column('venue', sa.String(200), nullable=True, comment='会议/期刊'),
        sa.Column('arxiv_id', sa.String(50), nullable=True, comment='arXiv ID'),
        sa.Column('doi', sa.String(100), nullable=True, comment='DOI'),
        sa.Column('citations_count', sa.Integer(), nullable=False, server_default='0', comment='引用数'),
        sa.Column('read_count', sa.Integer(), nullable=False, server_default='0', comment='阅读次数'),
        sa.Column('pdf_path', sa.String(500), nullable=True, comment='PDF存储路径'),
        sa.Column('pdf_url', sa.String(500), nullable=True, comment='PDF在线URL'),
        sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), 
                  nullable=False, comment='创建时间'),
        sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), 
                  nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('paper_id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # 创建paper_metadata表索引
    op.create_index('idx_year', 'paper_metadata', ['year'])
    op.create_index('idx_venue', 'paper_metadata', ['venue'])
    op.create_index('idx_arxiv_id', 'paper_metadata', ['arxiv_id'], unique=True)
    op.create_index('idx_doi', 'paper_metadata', ['doi'], unique=True)
    
    # 6. 创建task_status表
    op.create_table(
        'task_status',
        sa.Column('task_id', sa.String(100), nullable=False, comment='Celery任务ID'),
        sa.Column('user_id', sa.String(50), nullable=False, comment='用户ID'),
        sa.Column('task_type', sa.String(50), nullable=False, comment='任务类型'),
        sa.Column('task_name', sa.String(200), nullable=False, comment='任务名称'),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending', comment='任务状态'),
        sa.Column('params', mysql.JSON(), nullable=True, comment='任务参数'),
        sa.Column('result', mysql.JSON(), nullable=True, comment='任务结果'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0', comment='进度'),
        sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), 
                  nullable=False, comment='创建时间'),
        sa.Column('started_at', mysql.TIMESTAMP(), nullable=True, comment='开始时间'),
        sa.Column('completed_at', mysql.TIMESTAMP(), nullable=True, comment='完成时间'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # 创建task_status表索引
    op.create_index('idx_user_status', 'task_status', ['user_id', 'status'])
    op.create_index('idx_task_type', 'task_status', ['task_type'])
    op.create_index('idx_created', 'task_status', ['created_at'])
    
    # 7. 创建user_feedback表
    op.create_table(
        'user_feedback',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('user_id', sa.String(50), nullable=True, comment='用户ID'),
        sa.Column('feedback_type', sa.String(20), nullable=False, comment='反馈类型'),
        sa.Column('content', sa.Text(), nullable=False, comment='反馈内容'),
        sa.Column('rating', sa.Integer(), nullable=True, comment='评分'),
        sa.Column('related_chat_id', sa.BigInteger(), nullable=True, comment='关联的聊天记录ID'),
        sa.Column('related_paper_id', sa.String(100), nullable=True, comment='关联的论文ID'),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending', comment='处理状态'),
        sa.Column('admin_reply', sa.Text(), nullable=True, comment='管理员回复'),
        sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), 
                  nullable=False, comment='创建时间'),
        sa.Column('resolved_at', mysql.TIMESTAMP(), nullable=True, comment='解决时间'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # 创建user_feedback表索引
    op.create_index('idx_user_feedback', 'user_feedback', ['user_id', 'created_at'])
    op.create_index('idx_type_status', 'user_feedback', ['feedback_type', 'status'])


def downgrade() -> None:
    """删除所有表"""
    op.drop_table('user_feedback')
    op.drop_table('task_status')
    op.drop_table('paper_metadata')
    op.drop_table('reading_history')
    op.drop_table('chat_history')
    op.drop_table('user_profiles')
    op.drop_table('users')


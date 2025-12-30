"""
Project Service - 项目数据持久化服务

使用 SQLite 存储项目数据，支持 CRUD 操作
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from pathlib import Path

from models.project import Project, ProjectCreate, ProjectUpdate, PersonaSettings


# 数据库文件路径 - 指向项目根目录的 database 文件夹
DB_PATH = Path(__file__).parent.parent.parent / "database" / "projects.db"

# 确保 database 目录存在
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            industry TEXT DEFAULT '通用',
            avatar_letter TEXT DEFAULT '',
            avatar_color TEXT DEFAULT '#3B82F6',
            persona_settings TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            is_active INTEGER DEFAULT 0
        )
    """)
    
    # 创建用户-活跃项目映射表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_active_project (
            user_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # 创建索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at DESC)
    """)
    
    conn.commit()
    conn.close()


def row_to_project(row: sqlite3.Row) -> Project:
    """将数据库行转换为 Project 对象"""
    persona_data = json.loads(row['persona_settings']) if row['persona_settings'] else {}
    
    return Project(
        id=UUID(row['id']),
        user_id=row['user_id'],
        name=row['name'],
        industry=row['industry'] or '通用',
        avatar_letter=row['avatar_letter'] or '',
        avatar_color=row['avatar_color'] or '#3B82F6',
        persona_settings=PersonaSettings(**persona_data),
        created_at=datetime.fromisoformat(row['created_at']),
        updated_at=datetime.fromisoformat(row['updated_at']),
        is_active=bool(row['is_active'])
    )


def get_projects_by_user(user_id: str) -> List[Project]:
    """获取用户的所有项目，按更新时间倒序"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM projects 
        WHERE user_id = ? 
        ORDER BY updated_at DESC
    """, (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [row_to_project(row) for row in rows]


def get_project_by_id(project_id: UUID) -> Optional[Project]:
    """根据 ID 获取项目"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM projects WHERE id = ?", (str(project_id),))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row_to_project(row)
    return None


def create_project(user_id: str, data: ProjectCreate) -> Project:
    """创建新项目"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = datetime.now()
    project_id = uuid4()
    
    # 提取首字母作为头像显示
    avatar_letter = data.name[0].upper() if data.name else 'P'
    
    # 随机选择一个颜色（科技蓝色系）
    colors = ['#3B82F6', '#6366F1', '#8B5CF6', '#0EA5E9', '#14B8A6', '#F97316']
    import random
    avatar_color = random.choice(colors)
    
    # 处理人设配置
    persona_settings = data.persona_settings or PersonaSettings()
    
    cursor.execute("""
        INSERT INTO projects (id, user_id, name, industry, avatar_letter, avatar_color, persona_settings, created_at, updated_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(project_id),
        user_id,
        data.name,
        data.industry,
        avatar_letter,
        avatar_color,
        json.dumps(persona_settings.model_dump()),
        now.isoformat(),
        now.isoformat(),
        0
    ))
    
    conn.commit()
    conn.close()
    
    return Project(
        id=project_id,
        user_id=user_id,
        name=data.name,
        industry=data.industry,
        avatar_letter=avatar_letter,
        avatar_color=avatar_color,
        persona_settings=persona_settings,
        created_at=now,
        updated_at=now,
        is_active=False
    )


def update_project(project_id: UUID, data: ProjectUpdate) -> Optional[Project]:
    """更新项目"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 先获取现有项目
    project = get_project_by_id(project_id)
    if not project:
        conn.close()
        return None
    
    # 构建更新字段
    updates = []
    params = []
    
    if data.name is not None:
        updates.append("name = ?")
        params.append(data.name)
        updates.append("avatar_letter = ?")
        params.append(data.name[0].upper() if data.name else 'P')
    
    if data.industry is not None:
        updates.append("industry = ?")
        params.append(data.industry)
    
    if data.persona_settings is not None:
        updates.append("persona_settings = ?")
        params.append(json.dumps(data.persona_settings.model_dump()))
    
    if updates:
        now = datetime.now()
        updates.append("updated_at = ?")
        params.append(now.isoformat())
        params.append(str(project_id))
        
        cursor.execute(f"""
            UPDATE projects 
            SET {', '.join(updates)}
            WHERE id = ?
        """, params)
        
        conn.commit()
    
    conn.close()
    
    return get_project_by_id(project_id)


def delete_project(project_id: UUID) -> bool:
    """删除项目"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM projects WHERE id = ?", (str(project_id),))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return deleted


def get_active_project(user_id: str) -> Optional[UUID]:
    """获取用户当前激活的项目ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT project_id FROM user_active_project WHERE user_id = ?
    """, (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return UUID(row['project_id'])
    return None


def set_active_project(user_id: str, project_id: UUID) -> bool:
    """设置用户当前激活的项目"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = datetime.now()
    
    # 使用 REPLACE INTO 实现 upsert
    cursor.execute("""
        REPLACE INTO user_active_project (user_id, project_id, updated_at)
        VALUES (?, ?, ?)
    """, (user_id, str(project_id), now.isoformat()))
    
    # 更新项目的 updated_at 时间
    cursor.execute("""
        UPDATE projects SET updated_at = ? WHERE id = ?
    """, (now.isoformat(), str(project_id)))
    
    conn.commit()
    conn.close()
    
    return True


# 初始化数据库
init_db()



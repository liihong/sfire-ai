# 🔥 火源文案智能体 - 后端服务

> AI 驱动的短视频文案创作平台后端 API 服务

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 目录

- [项目简介](#项目简介)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [API 接口文档](#api-接口文档)
- [核心功能模块](#核心功能模块)
- [数据库设计](#数据库设计)
- [数据库扩展说明](#数据库扩展说明)
- [环境变量配置](#环境变量配置)
- [部署指南](#部署指南)

---

## 项目简介

**火源文案智能体** 是一个面向短视频创作者的 AI 辅助文案生成平台。后端服务基于 Python FastAPI 框架构建，集成多种大语言模型（LLM），提供智能化的内容创作能力。

### 核心特性

- 🤖 **多模型支持**: 集成 DeepSeek、Claude、豆包(火山引擎) 等主流 LLM
- 🎭 **智能体系统**: 6 种专业智能体，覆盖不同创作场景
- 👤 **IP 人设管理**: 支持多项目/多 IP 管理，个性化创作
- 📺 **抖音采集**: 集成 TikHub API，一键导入抖音账号画像
- ⚡ **流式输出**: 支持 SSE 流式响应，实时显示生成内容
- 🔐 **微信登录**: 支持微信小程序静默登录

---

## 技术栈

### 核心框架

| 技术 | 版本 | 说明 |
|------|------|------|
| **Python** | 3.10+ | 编程语言 |
| **FastAPI** | ≥0.109.0 | 高性能异步 Web 框架，自动生成 OpenAPI 文档 |
| **Uvicorn** | ≥0.27.0 | ASGI 服务器，支持热重载 |
| **Pydantic** | ≥2.5.0 | 数据验证和序列化 |

### HTTP 客户端

| 技术 | 版本 | 说明 |
|------|------|------|
| **httpx** | ≥0.26.0 | 现代异步 HTTP 客户端，用于调用外部 API |

### AI/LLM SDK

| 技术 | 版本 | 说明 |
|------|------|------|
| **OpenAI SDK** | ≥1.12.0 | 用于调用 DeepSeek API（兼容 OpenAI 格式）|

### 数据存储

| 技术 | 说明 |
|------|------|
| **SQLite** | 轻量级关系型数据库，当前项目存储方案 |

### 配置管理

| 技术 | 版本 | 说明 |
|------|------|------|
| **python-dotenv** | ≥1.0.0 | 环境变量管理，从 `.env` 文件加载配置 |

---

## 项目结构

```
backend/
├── main.py                    # 应用主入口，FastAPI 实例和核心路由
├── requirements.txt           # Python 依赖清单
├── env.example.txt            # 环境变量配置示例
├── projects.db                # SQLite 数据库文件（运行时生成）
│
├── constants/                 # 常量配置模块
│   ├── __init__.py
│   └── agents.py              # 智能体配置（System Prompts）
│
├── models/                    # 数据模型定义
│   ├── __init__.py
│   └── project.py             # 项目/IP 数据模型（Pydantic）
│
├── routers/                   # API 路由模块
│   ├── __init__.py
│   ├── generation.py          # 对话式创作生成接口
│   ├── project.py             # 项目管理 CRUD 接口
│   └── tikhub.py              # 抖音账号采集接口
│
├── services/                  # 业务逻辑层
│   ├── __init__.py
│   ├── llm_service.py         # LLM 服务（工厂模式）
│   └── project_service.py     # 项目数据持久化服务
│
├── scripts/                   # 工具脚本（待扩展）
├── venv/                      # Python 虚拟环境
└── __pycache__/               # Python 字节码缓存
```

---

## 快速开始

### 1. 环境要求

- Python 3.10 或更高版本
- pip 包管理器

### 2. 安装依赖

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制示例配置文件
cp env.example.txt .env

# 编辑 .env 文件，填入实际的 API Key
```

### 4. 启动服务

```bash
# 开发模式（热重载）
python main.py

# 或使用 uvicorn 直接启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## API 接口文档

### 接口总览

| 模块 | 路由前缀 | 说明 |
|------|----------|------|
| 健康检查 | `/` `/health` | 服务状态检查 |
| 认证 | `/api/auth/*` | 微信登录、用户信息 |
| 生成 | `/api/generate/*` | 文案生成、对话创作 |
| 项目 | `/api/projects/*` | 项目/IP 管理 CRUD |
| 采集 | `/api/tikhub/*` | 抖音账号采集分析 |

### 核心接口详情

#### 1. 对话式创作 `POST /api/generate/chat`

融合智能体人设和 IP 画像的流式对话生成接口。

**请求示例:**
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_type": "efficient_oral",
  "messages": [
    {"role": "user", "content": "帮我写一个关于健康饮食的短视频开头"}
  ],
  "model_type": "deepseek",
  "stream": true
}
```

**响应格式 (SSE 流式):**
```
data: {"content": "你"}
data: {"content": "知道"}
data: {"content": "吗？"}
...
data: {"done": true}
```

#### 2. 获取智能体列表 `GET /api/generate/agents`

返回所有可用的智能体类型。

#### 3. 项目管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/projects` | 获取项目列表 |
| POST | `/api/projects` | 创建新项目 |
| GET | `/api/projects/{id}` | 获取项目详情 |
| PUT | `/api/projects/{id}` | 更新项目 |
| DELETE | `/api/projects/{id}` | 删除项目 |
| POST | `/api/projects/switch` | 切换当前项目 |

#### 4. 抖音采集 `POST /api/tikhub/analyze-douyin`

分析抖音账号，提取 IP 画像信息。

**请求示例:**
```json
{
  "url": "https://www.douyin.com/user/MS4wLjABAAAA..."
}
```

---

## 核心功能模块

### 1. LLM 服务 (`services/llm_service.py`)

采用**工厂模式**设计，统一管理多种 LLM 提供商。

```python
# 类层次结构
BaseLLM (抽象基类)
├── DeepSeekLLM     # DeepSeek API (OpenAI 兼容格式)
├── ClaudeLLM       # Claude/Anthropic API
└── DoubaoLLM       # 豆包/火山引擎 API

# 使用示例
llm = LLMFactory.create("deepseek")
response = await llm.generate_text("你好", system_prompt="你是助手")
```

**支持的模型:**

| 模型 | 环境变量 | 默认端点 |
|------|----------|----------|
| DeepSeek | `DEEPSEEK_API_KEY` | api.deepseek.com |
| Claude | `CLAUDE_API_KEY` | api.anthropic.com |
| 豆包 | `DOUBAO_API_KEY` | ark.cn-beijing.volces.com |

### 2. 智能体系统 (`constants/agents.py`)

预设 6 种专业智能体，每种智能体包含专属的 System Prompt、温度参数等配置。

| 智能体 | 类型标识 | 特点 |
|--------|----------|------|
| ⚡ 高效口播 | `efficient_oral` | 黄金三秒开头，语言犀利 |
| 💝 情感共鸣 | `emotional` | 讲故事，文字细腻 |
| 📚 知识科普 | `knowledge` | 逻辑清晰，善用比喻 |
| 📖 故事叙述 | `story_telling` | 情节跌宕，引人入胜 |
| 🛒 带货种草 | `sales` | 精通消费心理 |
| 🔥 争议话题 | `controversial` | 观点鲜明，引发讨论 |

### 3. 项目管理 (`models/project.py` + `services/project_service.py`)

支持多项目/多 IP 管理，每个项目包含：

- **基础信息**: 名称、行业赛道、头像
- **人设配置** (`PersonaSettings`):
  - 语气风格 (tone)
  - 口头禅 (catchphrase)
  - 目标受众 (target_audience)
  - 对标账号 (benchmark_accounts)
  - 内容风格 (content_style)
  - 禁忌词 (taboos)
  - 常用关键词 (keywords)
  - IP 简介 (introduction)

---

## 数据库设计

### 当前架构 (SQLite)

#### 表结构

**projects 表** - 项目/IP 信息
```sql
CREATE TABLE projects (
    id TEXT PRIMARY KEY,              -- UUID 主键
    user_id TEXT NOT NULL,            -- 关联用户 ID
    name TEXT NOT NULL,               -- 项目名称
    industry TEXT DEFAULT '通用',      -- 赛道
    avatar_letter TEXT DEFAULT '',    -- 头像显示字符
    avatar_color TEXT DEFAULT '#3B82F6', -- 头像背景色
    persona_settings TEXT DEFAULT '{}', -- 人设配置 (JSON)
    created_at TEXT NOT NULL,         -- 创建时间
    updated_at TEXT NOT NULL,         -- 更新时间
    is_active INTEGER DEFAULT 0       -- 是否激活
);
```

**user_active_project 表** - 用户当前激活项目
```sql
CREATE TABLE user_active_project (
    user_id TEXT PRIMARY KEY,         -- 用户 ID
    project_id TEXT NOT NULL,         -- 当前激活的项目 ID
    updated_at TEXT NOT NULL          -- 更新时间
);
```

**索引**
```sql
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_updated_at ON projects(updated_at DESC);
```

---

## 数据库扩展说明

当前项目使用 SQLite 作为存储方案，适合开发和小规模部署。对于生产环境和更大规模的应用，建议进行以下扩展：

### 1. 迁移到 PostgreSQL / MySQL

#### 为什么迁移？

| 特性 | SQLite | PostgreSQL/MySQL |
|------|--------|------------------|
| 并发写入 | 有限 | 优秀 |
| 数据量 | 小型 | 大规模 |
| 复杂查询 | 基础 | 强大 |
| 高可用 | 不支持 | 主从复制、集群 |
| 连接池 | 不需要 | 需要 |

#### 迁移步骤

1. **安装数据库驱动**
```bash
# PostgreSQL
pip install asyncpg psycopg2-binary

# MySQL
pip install aiomysql pymysql
```

2. **修改环境变量**
```env
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/sfire_ai

# MySQL
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/sfire_ai
```

3. **引入 SQLAlchemy ORM**

推荐使用 SQLAlchemy 2.0 + asyncio 进行数据库操作重构：

```python
# models/database.py (新增)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

```python
# models/project.py (重构为 ORM 模型)
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

class ProjectORM(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String(100), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    industry = Column(String(50), default="通用")
    avatar_letter = Column(String(10), default="")
    avatar_color = Column(String(20), default="#3B82F6")
    persona_settings = Column(JSONB, default={})  # PostgreSQL JSONB
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=False)
```

### 2. 新增表结构建议

#### users 表 - 用户信息
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    openid VARCHAR(100) UNIQUE NOT NULL,      -- 微信 openid
    unionid VARCHAR(100),                      -- 微信 unionid
    nickname VARCHAR(50),
    avatar_url TEXT,
    phone VARCHAR(20),
    email VARCHAR(100),
    membership_level VARCHAR(20) DEFAULT 'free', -- 会员等级
    membership_expire_at TIMESTAMP,            -- 会员过期时间
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP
);
```

#### generation_history 表 - 生成记录
```sql
CREATE TABLE generation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    project_id UUID REFERENCES projects(id),
    agent_type VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    prompt TEXT NOT NULL,                     -- 用户输入
    response TEXT NOT NULL,                   -- AI 输出
    tokens_used INTEGER,                      -- 消耗的 token 数
    latency_ms INTEGER,                       -- 响应延迟
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- 索引
    INDEX idx_history_user (user_id),
    INDEX idx_history_project (project_id),
    INDEX idx_history_created (created_at DESC)
);
```

#### prompts 表 - 提示词模板
```sql
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),        -- NULL 表示系统预设
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),                      -- 分类
    content TEXT NOT NULL,                    -- 提示词内容
    is_public BOOLEAN DEFAULT FALSE,          -- 是否公开
    use_count INTEGER DEFAULT 0,              -- 使用次数
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### usage_quota 表 - 用量配额
```sql
CREATE TABLE usage_quota (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    quota_type VARCHAR(50) NOT NULL,          -- 'daily', 'monthly'
    total_quota INTEGER NOT NULL,             -- 总配额
    used_quota INTEGER DEFAULT 0,             -- 已使用
    reset_at TIMESTAMP NOT NULL,              -- 重置时间
    
    UNIQUE(user_id, quota_type)
);
```

### 3. 数据库迁移工具

推荐使用 **Alembic** 进行数据库版本管理：

```bash
# 安装
pip install alembic

# 初始化
alembic init migrations

# 生成迁移脚本
alembic revision --autogenerate -m "initial"

# 执行迁移
alembic upgrade head
```

### 4. 缓存层扩展

对于高频访问的数据，建议增加 Redis 缓存：

```bash
pip install redis aioredis
```

**缓存策略示例:**
```python
# services/cache_service.py
import aioredis

class CacheService:
    def __init__(self):
        self.redis = aioredis.from_url("redis://localhost:6379")
    
    async def get_project(self, project_id: str) -> Optional[dict]:
        cached = await self.redis.get(f"project:{project_id}")
        if cached:
            return json.loads(cached)
        return None
    
    async def set_project(self, project_id: str, data: dict, ttl: int = 3600):
        await self.redis.setex(
            f"project:{project_id}",
            ttl,
            json.dumps(data, ensure_ascii=False)
        )
```

### 5. 扩展架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI 应用                          │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐ │
│  │  Routers  │  │  Services │  │   Models  │  │  Utils   │ │
│  └───────────┘  └───────────┘  └───────────┘  └──────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     数据访问层 (DAL)                         │
│  ┌───────────────────────────────────────────────────────┐ │
│  │               SQLAlchemy ORM (async)                   │ │
│  └───────────────────────────────────────────────────────┘ │
├────────────────────────┬────────────────────────────────────┤
│       主数据库          │           缓存层                   │
│  ┌──────────────────┐  │  ┌────────────────────────────┐   │
│  │   PostgreSQL     │  │  │         Redis               │   │
│  │   - users        │  │  │  - 会话缓存                  │   │
│  │   - projects     │  │  │  - 项目缓存                  │   │
│  │   - history      │  │  │  - 配额计数                  │   │
│  │   - prompts      │  │  │  - 热点数据                  │   │
│  └──────────────────┘  │  └────────────────────────────┘   │
└────────────────────────┴────────────────────────────────────┘
```

---

## 环境变量配置

完整的环境变量配置请参考 `env.example.txt`：

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `HOST` | 否 | 服务监听地址，默认 `0.0.0.0` |
| `PORT` | 否 | 服务端口，默认 `8000` |
| `WX_APP_ID` | 是* | 微信小程序 AppID |
| `WX_APP_SECRET` | 是* | 微信小程序 AppSecret |
| `JWT_SECRET_KEY` | 是 | JWT 签名密钥 |
| `DEEPSEEK_API_KEY` | 是 | DeepSeek API 密钥 |
| `CLAUDE_API_KEY` | 否 | Claude API 密钥 |
| `DOUBAO_API_KEY` | 否 | 豆包 API 密钥 |
| `TIKHUB_API_KEY` | 否 | TikHub API 密钥（抖音采集） |
| `DATABASE_URL` | 否 | 数据库连接字符串 |

> *注：当前微信登录为 Mock 实现，生产环境需配置真实值

---

## 部署指南

### Docker 部署（推荐）

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
    volumes:
      - ./database:/app/database
```

### 生产环境建议

1. **使用 Gunicorn 作为进程管理器**
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **配置 Nginx 反向代理**
```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # SSE 支持
        proxy_buffering off;
        proxy_cache off;
    }
}
```

3. **日志和监控**
   - 集成 Sentry 进行错误追踪
   - 使用 Prometheus + Grafana 监控服务指标

---

## 开发计划

- [ ] 完善用户认证系统（微信真实登录）
- [ ] 引入 SQLAlchemy ORM
- [ ] 迁移至 PostgreSQL
- [ ] 添加 Redis 缓存层
- [ ] 生成历史记录和统计
- [ ] 用户配额管理
- [ ] 提示词模板市场
- [ ] API 限流和防护

---

## License

MIT License © 2024 火源文案智能体

---

<p align="center">
  Made with ❤️ by 火源团队
</p>


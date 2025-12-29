"""
Project Model - 项目（IP）数据模型

定义项目/IP的数据结构，用于多项目管理
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class PersonaSettings(BaseModel):
    """IP 人设配置"""
    tone: str = Field(default="专业亲和", description="语气风格：专业亲和/幽默风趣/严肃正式等")
    catchphrase: str = Field(default="", description="口头禅")
    target_audience: str = Field(default="", description="目标受众")
    benchmark_accounts: List[str] = Field(default_factory=list, description="对标账号列表")
    content_style: str = Field(default="", description="内容风格描述")
    taboos: List[str] = Field(default_factory=list, description="内容禁忌")
    keywords: List[str] = Field(default_factory=list, description="常用关键词")
    introduction: str = Field(default="", description="IP 简介")


class Project(BaseModel):
    """项目/IP 主模型"""
    id: UUID = Field(default_factory=uuid4, description="项目唯一标识")
    user_id: str = Field(..., description="关联用户ID")
    name: str = Field(..., description="项目名称，如'李医生科普IP'")
    industry: str = Field(default="通用", description="赛道，如'医疗健康'、'教育培训'等")
    avatar_letter: str = Field(default="", description="项目首字母/头像显示字符")
    avatar_color: str = Field(default="#3B82F6", description="头像背景色")
    persona_settings: PersonaSettings = Field(default_factory=PersonaSettings, description="人设配置")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    is_active: bool = Field(default=True, description="是否为当前激活项目")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class ProjectCreate(BaseModel):
    """创建项目请求模型"""
    name: str = Field(..., min_length=1, max_length=50, description="项目名称")
    industry: str = Field(default="通用", description="赛道")
    persona_settings: Optional[PersonaSettings] = Field(default=None, description="人设配置")


class ProjectUpdate(BaseModel):
    """更新项目请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="项目名称")
    industry: Optional[str] = Field(None, description="赛道")
    persona_settings: Optional[PersonaSettings] = Field(None, description="人设配置")


class ProjectSwitchRequest(BaseModel):
    """切换项目请求模型"""
    project_id: UUID = Field(..., description="要切换到的项目ID")


class ProjectListResponse(BaseModel):
    """项目列表响应模型"""
    success: bool = True
    projects: List[Project] = Field(default_factory=list, description="项目列表")
    active_project_id: Optional[UUID] = Field(None, description="当前激活的项目ID")


class ProjectResponse(BaseModel):
    """单个项目响应模型"""
    success: bool = True
    project: Project = Field(..., description="项目详情")


# 预设行业/赛道选项
INDUSTRY_OPTIONS = [
    "通用",
    "医疗健康",
    "教育培训",
    "金融理财",
    "科技互联网",
    "电商零售",
    "餐饮美食",
    "旅游出行",
    "房产家居",
    "美妆护肤",
    "母婴育儿",
    "体育健身",
    "娱乐影视",
    "游戏动漫",
    "法律咨询",
    "职场成长",
    "情感心理",
    "三农乡村",
    "其他"
]

# 预设语气风格选项
TONE_OPTIONS = [
    "专业亲和",
    "幽默风趣",
    "严肃正式",
    "温暖治愈",
    "犀利直接",
    "娓娓道来",
    "激情澎湃",
    "冷静理性"
]



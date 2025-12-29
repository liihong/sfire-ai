"""
Project Router - 项目管理 API 路由

提供项目的 CRUD 操作接口
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Request, Query

from models.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectSwitchRequest,
    ProjectListResponse,
    ProjectResponse,
    PersonaSettings,
    INDUSTRY_OPTIONS,
    TONE_OPTIONS
)
from services.project_service import (
    get_projects_by_user,
    get_project_by_id,
    create_project,
    update_project,
    delete_project,
    get_active_project,
    set_active_project
)


router = APIRouter(prefix="/api/projects", tags=["Projects"])


def get_user_id_from_request(request: Request) -> str:
    """
    从请求中提取用户ID
    
    注意：这是 Mock 实现，生产环境应该从 JWT Token 中解析
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # Mock: 使用 token 的前 16 位作为用户标识
        if token:
            return f"user_{token[:16]}"
    
    # 默认返回一个测试用户 ID
    return "user_default_mock"


@router.get("", response_model=ProjectListResponse)
async def list_projects(request: Request):
    """
    获取当前用户的所有项目列表
    
    按最后修改时间倒序排列
    """
    user_id = get_user_id_from_request(request)
    
    projects = get_projects_by_user(user_id)
    active_project_id = get_active_project(user_id)
    
    return ProjectListResponse(
        success=True,
        projects=projects,
        active_project_id=active_project_id
    )


@router.post("", response_model=ProjectResponse)
async def create_new_project(request: Request, data: ProjectCreate):
    """
    创建新项目
    
    - **name**: 项目名称（必填）
    - **industry**: 赛道（可选，默认"通用"）
    - **persona_settings**: 人设配置（可选）
    """
    user_id = get_user_id_from_request(request)
    
    try:
        project = create_project(user_id, data)
        return ProjectResponse(success=True, project=project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建项目失败: {str(e)}")


@router.get("/active", response_model=ProjectResponse)
async def get_active_project_info(request: Request):
    """
    获取当前激活的项目详情
    """
    user_id = get_user_id_from_request(request)
    
    active_id = get_active_project(user_id)
    if not active_id:
        raise HTTPException(status_code=404, detail="没有激活的项目")
    
    project = get_project_by_id(active_id)
    if not project:
        raise HTTPException(status_code=404, detail="激活的项目不存在")
    
    return ProjectResponse(success=True, project=project)


@router.post("/switch")
async def switch_project(request: Request, data: ProjectSwitchRequest):
    """
    切换当前激活的项目
    
    记录用户当前选中的 project_id
    """
    user_id = get_user_id_from_request(request)
    
    # 验证项目是否存在
    project = get_project_by_id(data.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 验证项目属于当前用户
    if project.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此项目")
    
    set_active_project(user_id, data.project_id)
    
    return {
        "success": True,
        "message": f"已切换到项目: {project.name}",
        "project": project
    }


@router.get("/options")
async def get_project_options():
    """
    获取项目配置选项
    
    返回可用的行业赛道和语气风格选项
    """
    return {
        "success": True,
        "industries": INDUSTRY_OPTIONS,
        "tones": TONE_OPTIONS
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(request: Request, project_id: UUID):
    """
    获取指定项目详情
    """
    user_id = get_user_id_from_request(request)
    
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 验证项目属于当前用户
    if project.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此项目")
    
    return ProjectResponse(success=True, project=project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_info(request: Request, project_id: UUID, data: ProjectUpdate):
    """
    更新项目信息
    """
    user_id = get_user_id_from_request(request)
    
    # 验证项目存在且属于当前用户
    existing = get_project_by_id(project_id)
    if not existing:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    if existing.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权修改此项目")
    
    project = update_project(project_id, data)
    if not project:
        raise HTTPException(status_code=500, detail="更新项目失败")
    
    return ProjectResponse(success=True, project=project)


@router.delete("/{project_id}")
async def delete_project_by_id(request: Request, project_id: UUID):
    """
    删除项目
    """
    user_id = get_user_id_from_request(request)
    
    # 验证项目存在且属于当前用户
    existing = get_project_by_id(project_id)
    if not existing:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    if existing.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权删除此项目")
    
    success = delete_project(project_id)
    
    return {
        "success": success,
        "message": "项目已删除" if success else "删除失败"
    }



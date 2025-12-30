"""
Generation Router - 对话式创作生成接口

提供智能体驱动的流式对话生成功能
"""

import json
from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from services.llm_service import LLMFactory
from services.project_service import get_project_by_id
from constants.agents import get_agent_config, get_all_agents, AgentType


router = APIRouter(prefix="/api/generate", tags=["Generation"])


# ============== Request/Response Models ==============

class ChatMessage(BaseModel):
    """对话消息模型"""
    role: str = Field(..., description="消息角色: 'user' 或 'assistant'")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """对话式创作请求模型"""
    project_id: Optional[str] = Field(
        default=None,
        description="项目ID，用于获取IP人设信息"
    )
    agent_type: str = Field(
        default=AgentType.EFFICIENT_ORAL,
        description="智能体类型"
    )
    messages: List[ChatMessage] = Field(
        ...,
        description="对话历史消息列表"
    )
    model_type: str = Field(
        default="deepseek",
        description="LLM模型类型: 'deepseek', 'claude', 'doubao'"
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="生成温度，不设置则使用智能体默认值"
    )
    max_tokens: int = Field(
        default=2048,
        ge=1,
        le=8192,
        description="最大生成tokens"
    )
    stream: bool = Field(
        default=True,
        description="是否启用流式输出"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "project_id": "550e8400-e29b-41d4-a716-446655440000",
                    "agent_type": "efficient_oral",
                    "messages": [
                        {"role": "user", "content": "帮我写一个关于健康饮食的短视频开头"}
                    ],
                    "model_type": "deepseek",
                    "stream": True
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """对话响应模型（非流式）"""
    success: bool = True
    content: str = Field(..., description="生成的内容")
    agent_type: str = Field(..., description="使用的智能体类型")
    model_type: str = Field(..., description="使用的模型类型")


class AgentInfo(BaseModel):
    """智能体信息模型"""
    type: str
    name: str
    icon: str
    description: str


class AgentListResponse(BaseModel):
    """智能体列表响应"""
    success: bool = True
    agents: List[AgentInfo]


# ============== Helper Functions ==============

def build_ip_persona_prompt(project) -> str:
    """
    从项目信息构建IP人设提示词
    
    Args:
        project: 项目对象
        
    Returns:
        IP人设提示词字符串
    """
    if not project:
        return ""
    
    persona = project.persona_settings
    parts = []
    
    parts.append(f"【IP信息】")
    parts.append(f"- IP名称：{project.name}")
    parts.append(f"- 所属赛道：{project.industry}")
    
    if persona.introduction:
        parts.append(f"- IP简介：{persona.introduction}")
    
    if persona.tone:
        parts.append(f"- 语气风格：{persona.tone}")
    
    if persona.target_audience:
        parts.append(f"- 目标受众：{persona.target_audience}")
    
    if persona.content_style:
        parts.append(f"- 内容风格：{persona.content_style}")
    
    if persona.catchphrase:
        parts.append(f"- 常用口头禅：{persona.catchphrase}")
    
    if persona.keywords:
        parts.append(f"- 常用关键词：{', '.join(persona.keywords)}")
    
    if persona.taboos:
        parts.append(f"- 内容禁忌：{', '.join(persona.taboos)}")
    
    if persona.benchmark_accounts:
        parts.append(f"- 对标账号：{', '.join(persona.benchmark_accounts)}")
    
    return "\n".join(parts)


def build_final_system_prompt(
    agent_system_prompt: str,
    ip_persona_prompt: str,
) -> str:
    """
    融合智能体人设和IP画像，构建最终的System Prompt
    
    Args:
        agent_system_prompt: 智能体基础系统提示词
        ip_persona_prompt: IP人设提示词
        
    Returns:
        融合后的最终系统提示词
    """
    parts = [agent_system_prompt]
    
    if ip_persona_prompt:
        parts.append("\n\n" + "=" * 40)
        parts.append("\n在创作时，请严格遵循以下IP人设设定，确保内容符合该IP的风格特点：\n")
        parts.append(ip_persona_prompt)
        parts.append("\n" + "=" * 40)
        parts.append("\n请在保持智能体专业能力的同时，融入以上IP的人设特点进行创作。")
    
    return "".join(parts)


def format_messages_for_llm(messages: List[ChatMessage]) -> str:
    """
    将消息列表格式化为用于LLM的prompt
    
    Args:
        messages: 消息列表
        
    Returns:
        格式化后的prompt字符串
    """
    # 返回最后一条用户消息作为prompt
    # 历史消息将作为上下文添加到system prompt中
    for msg in reversed(messages):
        if msg.role == "user":
            return msg.content
    
    return messages[-1].content if messages else ""


def build_conversation_context(messages: List[ChatMessage]) -> str:
    """
    构建对话上下文，用于多轮对话
    
    Args:
        messages: 消息列表
        
    Returns:
        对话上下文字符串
    """
    if len(messages) <= 1:
        return ""
    
    # 只取最近的历史消息（不包括最后一条）
    history = messages[:-1]
    if not history:
        return ""
    
    context_parts = ["\n【对话历史】"]
    for msg in history[-6:]:  # 最多保留最近6条历史记录
        role_name = "用户" if msg.role == "user" else "助手"
        context_parts.append(f"{role_name}：{msg.content}")
    
    context_parts.append("\n请基于以上对话历史，继续回复用户的最新请求。")
    
    return "\n".join(context_parts)


# ============== API Endpoints ==============

@router.get("/agents", response_model=AgentListResponse)
async def list_agents():
    """
    获取所有可用的智能体列表
    
    返回智能体的类型、名称、图标和描述信息
    """
    agents = get_all_agents()
    return AgentListResponse(
        success=True,
        agents=[AgentInfo(**agent) for agent in agents]
    )


@router.post("/chat")
async def generate_chat(request: ChatRequest):
    """
    对话式创作接口
    
    该接口融合了智能体人设和IP画像，提供流式对话生成功能。
    
    **工作流程**:
    1. 根据 project_id 获取IP人设信息
    2. 根据 agent_type 获取智能体基础System Prompt
    3. 融合 "IP画像" + "智能体人设" + "对话历史"
    4. 调用LLM进行生成
    
    **参数说明**:
    - **project_id**: 项目ID，用于获取IP人设（可选）
    - **agent_type**: 智能体类型（efficient_oral, emotional, knowledge等）
    - **messages**: 对话历史消息列表
    - **model_type**: LLM模型类型
    - **stream**: 是否启用流式输出（默认true）
    """
    try:
        # 1. 验证模型类型
        supported_models = LLMFactory.get_supported_models()
        if request.model_type.lower() not in supported_models:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的模型类型: '{request.model_type}'。支持的类型: {supported_models}"
            )
        
        # 2. 获取智能体配置
        try:
            agent_config = get_agent_config(request.agent_type)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # 3. 获取项目IP画像（如果提供了project_id）
        ip_persona_prompt = ""
        if request.project_id:
            try:
                project_uuid = UUID(request.project_id)
                project = get_project_by_id(project_uuid)
                if project:
                    ip_persona_prompt = build_ip_persona_prompt(project)
                else:
                    print(f"[Warning] 项目不存在: {request.project_id}")
            except ValueError:
                print(f"[Warning] 无效的项目ID格式: {request.project_id}")
        
        # 4. 构建最终System Prompt
        base_system_prompt = agent_config["system_prompt"]
        conversation_context = build_conversation_context(request.messages)
        
        final_system_prompt = build_final_system_prompt(
            agent_system_prompt=base_system_prompt + conversation_context,
            ip_persona_prompt=ip_persona_prompt,
        )
        
        # 5. 获取用户最新消息作为prompt
        user_prompt = format_messages_for_llm(request.messages)
        
        if not user_prompt:
            raise HTTPException(status_code=400, detail="消息列表不能为空")
        
        # 6. 确定生成参数
        temperature = request.temperature if request.temperature is not None else agent_config.get("temperature", 0.7)
        max_tokens = request.max_tokens or agent_config.get("max_tokens", 2048)
        
        # 7. 创建LLM实例
        llm = LLMFactory.create(request.model_type)
        
        # 8. 生成响应
        if request.stream:
            # 流式响应
            async def generate_stream():
                try:
                    async for chunk in llm.generate_stream(
                        prompt=user_prompt,
                        system_prompt=final_system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens
                    ):
                        # SSE格式输出
                        yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
                    
                    # 发送完成标记
                    yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"
                    
                except Exception as e:
                    error_msg = f"生成错误: {str(e)}"
                    yield f"data: {json.dumps({'error': error_msg}, ensure_ascii=False)}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",  # 禁用nginx缓冲
                }
            )
        else:
            # 非流式响应
            content = await llm.generate_text(
                prompt=user_prompt,
                system_prompt=final_system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return ChatResponse(
                success=True,
                content=content,
                agent_type=request.agent_type,
                model_type=request.model_type
            )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Chat generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"生成失败: {str(e)}"
        )


@router.post("/chat/quick")
async def quick_generate(
    content: str = Query(..., description="创作内容/主题"),
    agent_type: str = Query(default=AgentType.EFFICIENT_ORAL, description="智能体类型"),
    project_id: Optional[str] = Query(default=None, description="项目ID"),
    model_type: str = Query(default="deepseek", description="模型类型"),
):
    """
    快速创作接口（简化版）
    
    适用于单次生成场景，不需要维护对话历史。
    
    - **content**: 创作内容或主题
    - **agent_type**: 智能体类型
    - **project_id**: 项目ID（可选）
    - **model_type**: 模型类型
    """
    # 构建请求并调用chat接口
    request = ChatRequest(
        project_id=project_id,
        agent_type=agent_type,
        messages=[ChatMessage(role="user", content=content)],
        model_type=model_type,
        stream=False
    )
    
    return await generate_chat(request)


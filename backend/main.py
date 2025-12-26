"""
火源文案智能体 - Backend API

FastAPI application providing LLM-powered content generation services.
"""

import os
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json as json_module

from services.llm_service import LLMFactory

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 火源文案智能体 Backend starting...")
    print(f"📦 Supported LLM models: {LLMFactory.get_supported_models()}")
    # #region agent log
    import os
    log_dir = r"e:\project\sfire-ai\.cursor"
    log_file = os.path.join(log_dir, "debug.log")
    os.makedirs(log_dir, exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write('{"message":"Backend started","timestamp":' + str(__import__('time').time()*1000) + '}\n')
    print(f"[DEBUG] Log file initialized at: {log_file}")
    # #endregion
    yield
    # Shutdown
    print("👋 Backend shutting down...")


app = FastAPI(
    title="火源文案智能体 API",
    description="AI-powered content generation backend service",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# #region agent log
from starlette.middleware.base import BaseHTTPMiddleware

class DebugMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Log every incoming request
        log_entry = json_module.dumps({
            "location": "main.py:DebugMiddleware",
            "message": "Incoming request",
            "data": {
                "method": request.method,
                "path": str(request.url.path),
                "query": str(request.url.query),
                "content_type": request.headers.get("content-type", "none")
            },
            "timestamp": __import__('time').time() * 1000,
            "sessionId": "debug-session"
        })
        print(f"[DEBUG] MIDDLEWARE: {log_entry}")
        with open(r"e:\project\sfire-ai\.cursor\debug.log", "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
        
        response = await call_next(request)
        
        # Log response status
        print(f"[DEBUG] Response status: {response.status_code} for {request.url.path}")
        return response

app.add_middleware(DebugMiddleware)
# #endregion

# #region agent log
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Capture validation errors with full details for debugging."""
    try:
        body = await request.body()
        body_str = body.decode('utf-8') if body else 'empty'
    except:
        body_str = 'could not read body'
    
    log_data = {
        "location": "main.py:validation_exception_handler",
        "message": "Request validation error",
        "data": {
            "errors": str(exc.errors()),
            "body": body_str,
            "url": str(request.url)
        },
        "timestamp": __import__('time').time() * 1000,
        "sessionId": "debug-session",
        "hypothesisId": "D,E"
    }
    print(f"[DEBUG] VALIDATION ERROR: {json_module.dumps(log_data)}")
    log_entry = json_module.dumps(log_data)
    with open(r"e:\project\sfire-ai\.cursor\debug.log", "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")
    
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body_received": body_str}
    )
# #endregion


# ============== Request/Response Models ==============

class GenerateRequest(BaseModel):
    """Request model for text generation."""
    prompt: str = Field(..., description="The input prompt for generation")
    model_type: str = Field(
        default="deepseek",
        description="LLM model type: 'deepseek' or 'doubao'"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Optional system prompt to set context"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0.0-2.0)"
    )
    max_tokens: int = Field(
        default=2048,
        ge=1,
        le=8192,
        description="Maximum tokens to generate"
    )
    stream: bool = Field(
        default=False,
        description="Enable streaming response"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "写一段关于AI数字人的营销文案",
                    "model_type": "deepseek",
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "stream": False
                }
            ]
        }
    }


class GenerateResponse(BaseModel):
    """Response model for text generation."""
    success: bool = Field(..., description="Whether the request was successful")
    content: str = Field(..., description="Generated content")
    model_type: str = Field(..., description="The LLM model used")
    usage: Optional[dict] = Field(default=None, description="Token usage statistics")


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")


# ============== API Endpoints ==============

@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "service": "火源文案智能体 API",
        "status": "running",
        "version": "1.0.0",
        "supported_models": LLMFactory.get_supported_models()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# #region agent log
@app.get("/api/debug-test")
async def debug_test():
    """Test endpoint to verify logging works."""
    import os
    log_file = r"e:\project\sfire-ai\.cursor\debug.log"
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write('{"message":"debug-test endpoint called","timestamp":' + str(__import__('time').time()*1000) + '}\n')
        return {"status": "ok", "log_file": log_file, "message": "Log written successfully"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
# #endregion


@app.get("/api/models")
async def get_supported_models():
    """Get list of supported LLM models."""
    return {
        "models": LLMFactory.get_supported_models(),
        "default": "deepseek"
    }


@app.post(
    "/api/generate",
    response_model=GenerateResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def generate_content(request: GenerateRequest):
    """
    Generate content using the specified LLM model.
    
    This endpoint supports both DeepSeek and Doubao (火山引擎) models.
    
    - **prompt**: The input text for generation
    - **model_type**: Choose 'deepseek' or 'doubao'
    - **system_prompt**: Optional system context
    - **temperature**: Controls randomness (0.0-2.0)
    - **max_tokens**: Maximum length of generated content
    - **stream**: Enable streaming response (returns SSE)
    """
    # #region agent log
    import json
    log_data = {"location":"main.py:generate_content","message":"Request received","data":{"prompt_len":len(request.prompt),"model_type":request.model_type,"temperature":request.temperature,"max_tokens":request.max_tokens,"stream":request.stream},"timestamp":__import__('time').time()*1000,"sessionId":"debug-session","hypothesisId":"B,E"}
    print(f"[DEBUG] {json.dumps(log_data)}")
    log_entry = json.dumps(log_data)
    with open(r"e:\project\sfire-ai\.cursor\debug.log", "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")
    # #endregion
    try:
        # Validate model type
        supported_models = LLMFactory.get_supported_models()
        if request.model_type.lower() not in supported_models:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported model type: '{request.model_type}'. "
                       f"Supported: {supported_models}"
            )
        
        # Create LLM instance using factory
        llm = LLMFactory.create(request.model_type)
        
        # Handle streaming response
        if request.stream:
            async def generate_stream():
                async for chunk in llm.generate_stream(
                    prompt=request.prompt,
                    system_prompt=request.system_prompt,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                ):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        
        # Non-streaming response
        content = await llm.generate_text(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return GenerateResponse(
            success=True,
            content=content,
            model_type=request.model_type
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )


# ============== Content Generation Shortcuts ==============

@app.post("/api/generate/copywriting")
async def generate_copywriting(
    topic: str = Query(..., description="文案主题"),
    style: str = Query(default="营销", description="文案风格：营销/种草/科普/故事"),
    model_type: str = Query(default="deepseek", description="模型类型"),
    max_tokens: int = Query(default=1024, description="最大长度")
):
    """
    Generate marketing copywriting for the given topic.
    
    Specialized endpoint for content creation.
    """
    system_prompt = f"""你是一位专业的文案创作专家，擅长{style}类型的内容创作。
请根据用户提供的主题，创作一段吸引人的文案。
要求：
1. 内容要有吸引力和感染力
2. 语言流畅自然
3. 适合在社交媒体传播
4. 包含适当的情感表达"""
    
    prompt = f"请为以下主题创作一段{style}文案：\n\n主题：{topic}"
    
    request = GenerateRequest(
        prompt=prompt,
        model_type=model_type,
        system_prompt=system_prompt,
        max_tokens=max_tokens
    )
    
    return await generate_content(request)


@app.post("/api/generate/script")
async def generate_script(
    topic: str = Query(..., description="视频主题"),
    duration: str = Query(default="60秒", description="视频时长：30秒/60秒/3分钟"),
    model_type: str = Query(default="deepseek", description="模型类型"),
    max_tokens: int = Query(default=2048, description="最大长度")
):
    """
    Generate video script for digital human.
    
    Creates structured scripts suitable for AI digital human videos.
    """
    system_prompt = f"""你是一位专业的短视频脚本创作专家。
请根据用户提供的主题，创作一个适合{duration}的口播脚本。
要求：
1. 开头要有吸引力的hook
2. 内容结构清晰，逻辑流畅
3. 语言适合口播，自然亲切
4. 结尾要有明确的行动号召（CTA）
5. 标注适当的情感和节奏提示"""
    
    prompt = f"请为以下主题创作一个{duration}的口播视频脚本：\n\n主题：{topic}"
    
    request = GenerateRequest(
        prompt=prompt,
        model_type=model_type,
        system_prompt=system_prompt,
        max_tokens=max_tokens
    )
    
    return await generate_content(request)


# ============== Run Server ==============

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )



"""
LLM Service Module - Factory Pattern Implementation

This module provides a unified interface for different LLM providers:
- DeepSeek (OpenAI compatible format)
- Doubao (Volcengine/火山引擎 API)
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, AsyncGenerator
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BaseLLM(ABC):
    """Abstract base class for LLM implementations."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text based on the given prompt.
        
        Args:
            prompt: The input prompt for text generation.
            **kwargs: Additional parameters for the API call.
            
        Returns:
            Generated text response.
        """
        pass
    
    @abstractmethod
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Generate text in streaming mode.
        
        Args:
            prompt: The input prompt for text generation.
            **kwargs: Additional parameters for the API call.
            
        Yields:
            Generated text chunks.
        """
        pass


class DeepSeekLLM(BaseLLM):
    """
    DeepSeek LLM implementation using OpenAI-compatible API format.
    
    API Documentation: https://platform.deepseek.com/api-docs
    """
    
    DEFAULT_BASE_URL = "https://api.deepseek.com"
    DEFAULT_MODEL = "deepseek-chat"
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        super().__init__(api_key or os.getenv("DEEPSEEK_API_KEY"))
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", self.DEFAULT_BASE_URL)
        self.model = model or os.getenv("DEEPSEEK_MODEL", self.DEFAULT_MODEL)
        
        if not self.api_key:
            raise ValueError("DeepSeek API key is required. Set DEEPSEEK_API_KEY environment variable.")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text using DeepSeek API (OpenAI compatible format).
        
        Args:
            prompt: The input prompt.
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Generated text response.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
            "stream": False
        }
        
        # Support system prompt
        if "system_prompt" in kwargs:
            payload["messages"].insert(0, {
                "role": "system",
                "content": kwargs["system_prompt"]
            })
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Generate text in streaming mode using DeepSeek API.
        
        Args:
            prompt: The input prompt.
            **kwargs: Additional parameters.
            
        Yields:
            Generated text chunks.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
            "stream": True
        }
        
        if "system_prompt" in kwargs:
            payload["messages"].insert(0, {
                "role": "system",
                "content": kwargs["system_prompt"]
            })
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            import json
                            chunk = json.loads(data)
                            content = chunk["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue


class DoubaoLLM(BaseLLM):
    """
    Doubao (豆包) LLM implementation using Volcengine (火山引擎) API.
    
    API Documentation: https://www.volcengine.com/docs/82379
    """
    
    DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
    DEFAULT_MODEL = "ep-20241226000000-00000"  # Replace with actual endpoint ID
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        super().__init__(api_key or os.getenv("DOUBAO_API_KEY"))
        self.base_url = base_url or os.getenv("DOUBAO_BASE_URL", self.DEFAULT_BASE_URL)
        self.model = model or os.getenv("DOUBAO_MODEL", self.DEFAULT_MODEL)
        
        if not self.api_key:
            raise ValueError("Doubao API key is required. Set DOUBAO_API_KEY environment variable.")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text using Volcengine Doubao API.
        
        Args:
            prompt: The input prompt.
            **kwargs: Additional parameters.
            
        Returns:
            Generated text response.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
            "stream": False
        }
        
        if "system_prompt" in kwargs:
            payload["messages"].insert(0, {
                "role": "system",
                "content": kwargs["system_prompt"]
            })
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Generate text in streaming mode using Volcengine Doubao API.
        
        Args:
            prompt: The input prompt.
            **kwargs: Additional parameters.
            
        Yields:
            Generated text chunks.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
            "stream": True
        }
        
        if "system_prompt" in kwargs:
            payload["messages"].insert(0, {
                "role": "system",
                "content": kwargs["system_prompt"]
            })
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            import json
                            chunk = json.loads(data)
                            content = chunk["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue


class LLMFactory:
    """
    Factory class for creating LLM instances.
    
    Usage:
        llm = LLMFactory.create("deepseek")
        response = await llm.generate_text("Hello, world!")
    """
    
    _registry: Dict[str, type] = {
        "deepseek": DeepSeekLLM,
        "doubao": DoubaoLLM,
    }
    
    @classmethod
    def create(cls, model_type: str, **kwargs) -> BaseLLM:
        """
        Create an LLM instance based on the model type.
        
        Args:
            model_type: The type of LLM ('deepseek' or 'doubao').
            **kwargs: Additional arguments passed to the LLM constructor.
            
        Returns:
            An instance of the requested LLM.
            
        Raises:
            ValueError: If the model type is not supported.
        """
        model_type = model_type.lower().strip()
        
        if model_type not in cls._registry:
            supported = ", ".join(cls._registry.keys())
            raise ValueError(
                f"Unsupported model type: '{model_type}'. "
                f"Supported types: {supported}"
            )
        
        return cls._registry[model_type](**kwargs)
    
    @classmethod
    def register(cls, name: str, llm_class: type) -> None:
        """
        Register a new LLM class.
        
        Args:
            name: The name to register the LLM under.
            llm_class: The LLM class to register.
        """
        if not issubclass(llm_class, BaseLLM):
            raise TypeError(f"{llm_class} must be a subclass of BaseLLM")
        cls._registry[name.lower()] = llm_class
    
    @classmethod
    def get_supported_models(cls) -> list:
        """Return a list of supported model types."""
        return list(cls._registry.keys())



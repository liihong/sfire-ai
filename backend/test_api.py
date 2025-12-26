"""
API 测试脚本 - 用于验证 DeepSeek 和 Doubao API 是否正常工作
"""
import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_env_vars():
    """检查环境变量配置"""
    print("=" * 50)
    print("Environment Variables Check")
    print("=" * 50)
    
    # DeepSeek
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    print(f"DEEPSEEK_API_KEY: {'SET [OK]' if deepseek_key else 'NOT SET [X]'}")
    if deepseek_key:
        print(f"  - Length: {len(deepseek_key)} chars")
        print(f"  - Prefix: {deepseek_key[:8]}...")
    
    deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    print(f"DEEPSEEK_MODEL: {deepseek_model}")
    
    # Doubao
    doubao_key = os.getenv("DOUBAO_API_KEY")
    print(f"\nDOUBAO_API_KEY: {'SET [OK]' if doubao_key else 'NOT SET [X]'}")
    if doubao_key:
        print(f"  - Length: {len(doubao_key)} chars")
        print(f"  - Prefix: {doubao_key[:8]}...")
    
    doubao_model = os.getenv("DOUBAO_MODEL")
    print(f"DOUBAO_MODEL: {doubao_model if doubao_model else 'NOT SET (will use default)'}")
    
    doubao_base_url = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
    print(f"DOUBAO_BASE_URL: {doubao_base_url}")
    
    print("=" * 50)
    return deepseek_key, doubao_key

async def test_deepseek():
    """Test DeepSeek API"""
    print("\nTesting DeepSeek API...")
    try:
        from services.llm_service import LLMFactory
        llm = LLMFactory.create("deepseek")
        response = await llm.generate_text("Hello, introduce yourself in one sentence", max_tokens=50)
        print(f"[OK] DeepSeek API is working!")
        print(f"  Response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"[X] DeepSeek API error: {e}")
        return False

async def test_doubao():
    """Test Doubao API"""
    print("\nTesting Doubao API...")
    try:
        from services.llm_service import LLMFactory
        llm = LLMFactory.create("doubao")
        response = await llm.generate_text("Hello, introduce yourself in one sentence", max_tokens=50)
        print(f"[OK] Doubao API is working!")
        print(f"  Response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"[X] Doubao API error: {e}")
        return False

async def main():
    deepseek_key, doubao_key = check_env_vars()
    
    if deepseek_key:
        await test_deepseek()
    else:
        print("\nSkipping DeepSeek test (API Key not set)")
    
    if doubao_key:
        await test_doubao()
    else:
        print("\nSkipping Doubao test (API Key not set)")
        print("Please set DOUBAO_API_KEY in backend/.env file")

if __name__ == "__main__":
    asyncio.run(main())


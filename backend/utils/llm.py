"""
LLM接口封装 - 支持OpenAI和SambaNova
"""
from typing import List, Dict, Optional, Any
import json
from openai import OpenAI
from loguru import logger

from config.settings import settings


class LLMClient:
    """LLM客户端，支持多个提供商"""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        
        if self.provider == "openai":
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_API_BASE
            )
            self.model = settings.OPENAI_MODEL
        elif self.provider == "sambanova":
            self.client = OpenAI(
                api_key=settings.SAMBANOVA_API_KEY,
                base_url=settings.SAMBANOVA_API_BASE
            )
            self.model = settings.SAMBANOVA_MODEL
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
        logger.info(f"LLM客户端初始化完成: provider={self.provider}, model={self.model}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        对话接口
        
        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "..."}]
            temperature: 温度参数（可选）
            max_tokens: 最大token数（可选）
            response_format: 响应格式（可选，如 {"type": "json_object"}）
        
        Returns:
            LLM的回复文本
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens
            }
            
            # OpenAI支持response_format，SambaNova可能不支持
            if response_format and self.provider == "openai":
                kwargs["response_format"] = response_format
            
            response = self.client.chat.completions.create(**kwargs)
            
            content = response.choices[0].message.content
            
            # 记录token使用情况
            if hasattr(response, 'usage'):
                logger.debug(
                    f"Token使用: prompt={response.usage.prompt_tokens}, "
                    f"completion={response.usage.completion_tokens}, "
                    f"total={response.usage.total_tokens}"
                )
            
            return content
            
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise
    
    def chat_with_system(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None
    ) -> str:
        """
        简化的对话接口（带系统提示词）
        
        Args:
            system_prompt: 系统提示词
            user_message: 用户消息
            temperature: 温度参数
        
        Returns:
            LLM的回复
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        return self.chat(messages, temperature=temperature)
    
    def extract_json(
        self,
        prompt: str,
        user_input: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        从LLM响应中提取JSON
        
        Args:
            prompt: 提示词
            user_input: 用户输入
            max_retries: 最大重试次数
        
        Returns:
            解析后的JSON字典
        """
        for attempt in range(max_retries):
            try:
                # 构建消息
                messages = [
                    {"role": "system", "content": "你是一个数据提取专家，只输出JSON格式的结果，不要包含其他文字。"},
                    {"role": "user", "content": f"{prompt}\n\n用户输入：{user_input}"}
                ]
                
                # 调用LLM
                response = self.chat(messages, temperature=0.3)
                
                # 清理响应（移除可能的markdown标记）
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:]
                if response.startswith("```"):
                    response = response[3:]
                if response.endswith("```"):
                    response = response[:-3]
                response = response.strip()
                
                # 解析JSON
                result = json.loads(response)
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON解析失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                logger.debug(f"原始响应: {response}")
                
                if attempt == max_retries - 1:
                    # 最后一次尝试失败，返回空字典
                    logger.error("JSON提取失败，返回空字典")
                    return {}
            
            except Exception as e:
                logger.error(f"提取JSON时出错: {e}")
                if attempt == max_retries - 1:
                    return {}
        
        return {}
    
    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None
    ):
        """
        流式对话接口（生成器）
        
        Args:
            messages: 消息列表
            temperature: 温度参数
        
        Yields:
            每个token的文本片段
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"流式调用失败: {e}")
            raise


# 全局LLM客户端实例
_llm_client = None

def get_llm_client() -> LLMClient:
    """获取全局LLM客户端实例（单例模式）"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


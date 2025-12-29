# -*- coding: utf-8 -*-
"""
Agent 基类接口
定义所有 Agent 必须实现的公共接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Generator


class BaseAgent(ABC):
    """
    Agent 基类
    所有具体的 Agent 实现都应该继承此类并实现抽象方法
    """
    
    def __init__(self, name: str, description: str):
        """
        初始化 Agent
        
        Args:
            name: Agent 名称
            description: Agent 描述
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def get_system_prompt(self, location: Optional[Dict[str, float]] = None) -> str:
        """
        获取系统提示词
        
        Args:
            location: 用户位置信息（可选），包含 latitude 和 longitude
        
        Returns:
            系统提示词字符串
        """
        pass
    
    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        获取 Agent 可用的工具列表（OpenAI 格式）
        
        Returns:
            工具定义列表
        """
        pass
    
    @abstractmethod
    def stream_response(
        self,
        messages: List[Dict[str, Any]],
        session_id: str,
        location: Optional[Dict[str, float]] = None,
        email: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        流式生成响应
        
        Args:
            messages: 消息列表
            session_id: 会话ID
            location: 用户位置信息（可选）
            email: 用户邮箱（用于历史记录存储）
        
        Yields:
            str: SSE格式的流式响应数据
        """
        pass
    
    @abstractmethod
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        执行工具调用
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
        
        Returns:
            工具执行结果
        """
        pass
    
    def get_info(self) -> Dict[str, str]:
        """
        获取 Agent 信息
        
        Returns:
            包含 name 和 description 的字典
        """
        return {
            "name": self.name,
            "description": self.description
        }


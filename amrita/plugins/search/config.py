"""网页搜索插件配置"""

from typing import Literal

from pydantic import BaseModel, Field


class WebSearchConfig(BaseModel):
    """网页搜索配置"""

    enabled: bool = Field(default=True, description="是否启用网页搜索功能")

    default_engine: Literal["bing", "google", "duckduckgo", "baidu"] = Field(
        default="bing",
        description="默认搜索引擎"
    )

    max_results: int = Field(
        default=5,
        description="每次搜索返回的最大结果数",
        ge=1,
        le=20
    )

    search_timeout: int = Field(
        default=10,
        description="搜索超时时间（秒）",
        ge=5,
        le=60
    )

    require_permission: bool = Field(
        default=False,
        description="是否需要权限才能使用搜索功能"
    )

    api_keys: dict = Field(
        default_factory=dict,
        description="各搜索引擎的API密钥（如果需要）"
    )

    safe_search: bool = Field(
        default=True,
        description="是否启用安全搜索"
    )

    summarize_results: bool = Field(
        default=True,
        description="是否使用LLM总结搜索结果"
    )

    max_summary_length: int = Field(
        default=500,
        description="搜索结果总结的最大长度",
        ge=100,
        le=1000
    )

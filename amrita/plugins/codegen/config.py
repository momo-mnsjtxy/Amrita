"""代码生成插件配置"""

from typing import Any

from pydantic import BaseModel, Field


class CodeGenConfig(BaseModel):
    """代码生成插件配置"""

    enabled: bool = Field(default=True, description="是否启用代码生成功能")

    require_permission: str = Field(
        default="codegen.use",
        description="使用代码生成功能所需的权限节点"
    )

    default_language: str = Field(
        default="python",
        description="默认编程语言",
        examples=["python", "javascript", "java", "cpp", "go", "rust"]
    )

    allowed_languages: list[str] = Field(
        default_factory=lambda: [
            "python", "javascript", "typescript", "java", "cpp",
            "c", "bash", "shell", "go", "rust", "php", "ruby",
            "swift", "kotlin", "scala", "r", "matlab", "sql"
        ],
        description="支持生成代码的编程语言列表"
    )

    max_code_length: int = Field(
        default=2000,
        description="生成代码的最大长度（字符数）",
        ge=500,
        le=5000
    )

    include_explanations: bool = Field(
        default=True,
        description="是否在生成代码时包含解释和注释"
    )

    code_templates: list[dict[str, Any]] = Field(
        default_factory=lambda: [
            {
                "name": "function",
                "description": "生成函数",
                "prompt_template": "为以下需求生成一个{language}函数：\n\n需求：{description}\n\n功能：\n{features}\n\n要求：\n1. 包含适当的错误处理\n2. 添加文档字符串\n3. 包含输入验证"
            },
            {
                "name": "class",
                "description": "生成类",
                "prompt_template": "为以下需求生成一个{language}类：\n\n需求：{description}\n\n功能：\n{features}\n\n要求：\n1. 使用面向对象设计原则\n2. 包含适当的属性和方法\n3. 实现构造函数\n4. 添加文档字符串"
            },
            {
                "name": "script",
                "description": "生成完整脚本",
                "prompt_template": "为以下需求生成一个完整的{language}脚本：\n\n需求：{description}\n\n功能：\n{features}\n\n要求：\n1. 包含命令行接口\n2. 添加使用说明\n3. 处理各种错误情况\n4. 添加版本信息和作者"
            },
            {
                "name": "api",
                "description": "生成API接口",
                "prompt_template": "为以下需求生成一个{language} API接口：\n\n需求：{description}\n\n功能：\n{features}\n\n要求：\n1. 使用REST风格\n2. 包含错误处理\n3. 添加认证机制\n4. 支持日志记录"
            }
        ],
        description="代码模板配置"
    )

    optimization_level: str = Field(
        default="balanced",
        description="代码优化级别",
        examples=["simple", "balanced", "optimized"]
    )

    include_tests: bool = Field(
        default=False,
        description="是否生成测试代码"
    )

    safe_mode: bool = Field(
        default=True,
        description="是否启用安全模式（阻止生成恶意代码）"
    )

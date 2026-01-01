"""代码生成器核心模块"""

from typing import Any

from nonebot import logger, on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event
from nonebot.params import CommandArg

from amrita.plugins.chat import config as chat_config  # type: ignore
from amrita.plugins.chat.utils.libchat import chat_client  # type: ignore
from amrita.plugins.perm.command_manager import (
    local_manager as permission_manager,  # type: ignore
)

from .config import CodeGenConfig

# 加载配置
codegen_config = CodeGenConfig()

# 创建代码生成命令
code_cmd = on_command(
    "code",
    aliases={"代码生成", "生成代码", "codegen"},
    priority=5,
    block=True
)

class CodeGenerator:
    """代码生成器主类"""

    def __init__(self, config: CodeGenConfig):
        self.config = config

    async def generate_code(
        self,
        description: str,
        language: str | None = None,
        template: str = "function",
        features: str | None = None,
        include_explanations: bool = True
    ) -> dict[str, Any]:
        """
        生成代码

        Args:
            description: 代码需求描述
            language: 编程语言
            template: 使用的模板类型
            features: 额外功能要求
            include_explanations: 是否包含解释

        Returns:
            包含生成代码和元数据的字典
        """

        if not language:
            language = self.config.default_language

        # 验证语言是否允许
        if language not in self.config.allowed_languages:
            return {
                "code": "",
                "explanation": f"不支持的语言: {language}",
                "language": language,
                "success": False
            }

        # 查找合适的模板
        template_config = self._find_template(template)
        if not template_config:
            return {
                "code": "",
                "explanation": f"不支持的模板类型: {template}",
                "language": language,
                "success": False
            }

        # 构建提示词
        prompt = self._build_prompt(
            template_config["prompt_template"],
            language,
            description,
            features or "",
            include_explanations
        )

        try:
            # 调用LLM生成代码
            config = chat_config.get_chat_config()  # type: ignore
            if not config or not config.enabled:
                return {
                    "code": "",
                    "explanation": "聊天功能未启用或配置错误",
                    "language": language,
                    "success": False
                }

            system_prompt = self._get_system_prompt(language, include_explanations)
            response = await chat_client.chat(
                prompt=prompt,
                system=system_prompt,
                max_tokens=min(self.config.max_code_length, 2000),
                temperature=0.1  # 代码生成需要较低的温度值
            )

            if not response or not response.content:
                return {
                    "code": "",
                    "explanation": "代码生成失败：无法获取模型响应",
                    "language": language,
                    "success": False
                }

            # 解析生成的代码
            generated_content = response.content
            code, explanation = self._parse_generated_content(generated_content)

            return {
                "code": code,
                "explanation": explanation,
                "language": language,
                "success": True
            }

        except Exception as e:
            logger.error(f"代码生成失败: {e}")
            return {
                "code": "",
                "explanation": f"代码生成失败: {e!s}",
                "language": language,
                "success": False
            }

    def _find_template(self, template_name: str) -> dict[str, Any] | None:
        """查找模板配置"""
        for template in self.config.code_templates:
            if template.get("name") == template_name:
                return template
        return None

    def _build_prompt(
        self,
        template: str,
        language: str,
        description: str,
        features: str,
        include_explanations: bool
    ) -> str:
        """构建生成提示词"""
        prompt = template.format(
            language=language,
            description=description,
            features=features
        )

        # 添加优化要求
        if self.config.optimization_level == "simple":
            prompt += "\n\n优化要求：生成简单、易读的代码"
        elif self.config.optimization_level == "optimized":
            prompt += "\n\n优化要求：生成性能优化、高效的代码"
        else:  # balanced
            prompt += "\n\n优化要求：在可读性和性能之间取得平衡"

        # 添加测试代码要求
        if self.config.include_tests:
            prompt += "\n\n4. 包含单元测试代码"

        # 安全模式
        if self.config.safe_mode:
            prompt += (
                "\n\n重要安全要求：\n"
                "1. 不要生成恶意代码\n"
                "2. 不要生成可能破坏系统的代码\n"
                "3. 处理所有可能的异常情况\n"
                "4. 验证所有用户输入"
            )

        return prompt

    def _get_system_prompt(self, language: str, include_explanations: bool) -> str:
        """获取系统提示词"""
        base_prompt = f"你是一个专业的 {language} 代码生成助手。"

        if include_explanations:
            base_prompt += "生成代码时，请提供：\n1. 完整的可运行代码\n2. 详细的代码说明\n3. 使用示例\n4. 注意事项"
        else:
            base_prompt += "只生成代码，不包含额外解释。"

        return base_prompt

    def _parse_generated_content(self, content: str) -> tuple[str, str]:
        """解析生成的内容，分离代码和说明"""
        # 尝试分离代码块和说明
        lines = content.split("\n")
        code_lines = []
        explanation_lines = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                code_lines.append(line)
            else:
                explanation_lines.append(line)

        code = "\n".join(code_lines)
        explanation = "\n".join(explanation_lines).strip()

        # 如果没有找到代码块，将整个内容作为代码
        if not code:
            code = content
            explanation = ""

        return code, explanation


# 创建代码生成器实例
code_generator = CodeGenerator(codegen_config)

@code_cmd.handle()
async def handle_code_generation(event: Event, args: Message = CommandArg()):
    """处理代码生成请求"""

    if not codegen_config.enabled:
        await code_cmd.finish("代码生成功能已禁用")
        return

    # 权限检查
    if not await permission_manager.require_permission(event, codegen_config.require_permission):
        await code_cmd.finish(f"您没有使用代码生成功能的权限（需要权限: {codegen_config.require_permission}）")
        return

    # 解析参数
    arg_text = args.extract_plain_text().strip()
    if not arg_text:
        await code_cmd.finish(
            "请提供代码生成需求，例如：\n"
            "/code 生成一个Python函数，计算斐波那契数列\n"
            "/code --language=javascript --template=class 创建一个用户管理类\n\n"
            "可用参数：\n"
            "--language=<语言>   指定编程语言\n"
            "--template=<模板>   指定模板类型 (function, class, script, api)\n"
            "--features=<功能>   额外功能要求"
        )
        return

    # 解析命令行参数
    description, language, template, features = await _parse_arguments(arg_text)

    if not description:
        await code_cmd.finish("请提供代码生成需求描述")
        return

    await code_cmd.send(f"💻 正在生成代码（{language}，模板：{template}）...")

    # 生成代码
    result = await code_generator.generate_code(
        description=description,
        language=language,
        template=template,
        features=features,
        include_explanations=codegen_config.include_explanations
    )

    if not result["success"]:
        await code_cmd.finish(f"代码生成失败: {result['explanation']}")
        return

    # 构建回复
    reply = "✅ 代码生成成功\n"
    reply += f"📋 语言: {result['language']}\n"
    reply += f"📝 模板: {template}\n\n"

    if result["code"]:
        reply += f"```\n{result['language']}\n{result['code']}\n```\n\n"

    if result["explanation"]:
        explanation = result["explanation"][:500]  # 限制解释长度
        if len(result["explanation"]) > 500:
            explanation += "...（更多说明已省略）"
        reply += f"💡 说明:\n{explanation}\n"

    # 添加提示
    reply += "\n💡 提示：可以使用 /code help 查看详细用法"

    await code_cmd.finish(reply)

async def _parse_arguments(arg_text: str) -> tuple[str, str, str, str]:
    """解析命令行参数"""
    import re

    description = ""
    language = codegen_config.default_language
    template = "function"
    features = ""

    # 提取参数
    # --language=xxx
    lang_match = re.search(r"--language[=\s]?(\w+)", arg_text)
    if lang_match:
        language = lang_match.group(1)
        arg_text = arg_text.replace(lang_match.group(0), "")

    # --template=xxx
    template_match = re.search(r"--template[=\s]?(\w+)", arg_text)
    if template_match:
        template = template_match.group(1)
        arg_text = arg_text.replace(template_match.group(0), "")

    # --features=xxx
    features_match = re.search(r'--features[=\s]?"([^"]*)"', arg_text)
    if not features_match:
        features_match = re.search(r"--features[=\s]?'([^']*)'", arg_text)
    if not features_match:
        features_match = re.search(r"--features[=\s]?(.+?)(?=\s+--|$)", arg_text)

    if features_match:
        features = features_match.group(1).strip("'\" ")
        arg_text = arg_text.replace(features_match.group(0), "")

    # 剩余的是描述
    description = arg_text.strip()

    return description, language, template, features

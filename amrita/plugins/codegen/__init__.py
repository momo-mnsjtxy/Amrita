from nonebot.plugin import PluginMetadata, require

require("amrita.plugins.perm")
require("amrita.plugins.menu")

from . import (
    code_generator,
    config,
    templates,
)

__all__ = [
    "code_generator",
    "config",
    "templates",
]

__plugin_meta__ = PluginMetadata(
    name="代码生成插件",
    description="智能代码生成助手，支持多种编程语言",
    usage="使用 /code 命令生成代码，支持多种语言和框架",
    type="application",
)

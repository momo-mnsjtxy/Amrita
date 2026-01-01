from nonebot.plugin import PluginMetadata, require

require("amrita.plugins.perm")
require("amrita.plugins.menu")

from . import (
    command_executor,
    config,
    security,
)

__all__ = [
    "command_executor",
    "config",
    "security",
]

__plugin_meta__ = PluginMetadata(
    name="Linux命令执行插件",
    description="提供安全的Linux命令执行功能，支持权限控制和命令白名单",
    usage="使用 /cmd <命令> 执行Linux命令（需要相应权限）",
    type="application",
)

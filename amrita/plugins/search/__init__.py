from nonebot.plugin import PluginMetadata, require

require("amrita.plugins.perm")
require("amrita.plugins.menu")

from . import (
    config,
    search_command,
)

__all__ = [
    "config",
    "search_command",
]

__plugin_meta__ = PluginMetadata(
    name="网页搜索插件",
    description="提供网页搜索功能，支持多种搜索引擎",
    usage="使用 /search 命令进行网页搜索",
    type="application",
)

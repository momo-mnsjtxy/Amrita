"""MiniAgent 框架初始化模块

该模块是 MiniAgent（基于 Amrita）框架的入口点，负责导入和初始化核心组件。

上游项目：Amrita - https://github.com/LiteSuggarDEV/Amrita
"""

import nonebot
from nonebot import run

from . import cli
from .cmds import main as cmd_main
from .cmds import plugin
from .config import get_amrita_config
from .utils.bot_utils import init
from .utils.plugins import load_plugins
from .utils.utils import get_amrita_version

__all__ = [
    "cli",
    "cmd_main",
    "get_amrita_config",
    "get_amrita_version",
    "init",
    "load_plugins",
    "nonebot",
    "plugin",
    "run",
]

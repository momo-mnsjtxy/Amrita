"""MiniAgent 核心配置模块

该模块定义了 MiniAgent（基于 Amrita）机器人的核心配置模型和获取配置的方法。
"""

from typing import Literal

from nonebot import get_plugin_config, logger
from pydantic import BaseModel, model_validator


class AmritaConfig(BaseModel):
    """MiniAgent 核心配置模型（兼容保留 AmritaConfig 名称）"""

    # 日志目录
    log_dir: str = "logs"

    max_event_record: int = 1000

    # 管理员群组ID
    admin_group: int = -1

    # 禁用的内置插件列表
    disabled_builtin_plugins: list[Literal["chat", "manager", "perm", "menu"]] = []

    # MiniAgent 日志级别（配置键保持 amrita_log_level 以兼容历史配置）
    amrita_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = (
        "WARNING"
    )

    # 公开群组ID（Bot对外展示）
    public_group: int = 0

    # 机器人名称
    bot_name: str = "MiniAgent"

    # 请求速率限制（间隔秒）
    rate_limit: int = 5

    # 是否禁用内置菜单
    disable_builtin_menu: bool = False

    # 是否自动通过好友申请
    auto_approve_friend_request: bool = True

    # 是否自动通过拉群申请
    auto_approve_group_request: bool = True

    @model_validator(mode="after")
    def _vali(self):
        if 10000 > self.admin_group > 0:
            logger.warning("MiniAgent config 'admin_group' is invalid, set to -1")
            self.admin_group = -1
        if self.admin_group == -1:
            logger.info(
                "MiniAgent config 'admin_group' is disabled, so some push messages will just be printed to console."
            )
        return self


def get_amrita_config() -> AmritaConfig:
    """获取 MiniAgent 配置（兼容保留 get_amrita_config 名称）

    Returns:
        AmritaConfig: 配置对象
    """
    return get_plugin_config(AmritaConfig)

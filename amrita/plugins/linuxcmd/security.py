"""命令安全验证模块"""

import re
import shlex

from nonebot.log import logger

from .config import LinuxCmdConfig


class CommandSecurity:
    """命令安全验证器"""

    def __init__(self, config: LinuxCmdConfig):
        self.config = config
        self.blocked_patterns_compiled = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in config.blocked_patterns
        ]

    def validate_command(self, command: str, user_id: str = "", group_id: str = "") -> tuple[bool, str]:
        """
        验证命令是否可以执行

        Args:
            command: 要执行的命令
            user_id: 用户ID
            group_id: 群组ID

        Returns:
            (是否允许执行, 原因说明)
        """
        # 1. 检查用户是否被允许
        if self.config.allowed_users and user_id not in self.config.allowed_users:
            return False, "您的用户ID不在白名单中"

        # 2. 检查群组是否被允许
        if self.config.allowed_groups and group_id not in self.config.allowed_groups:
            return False, "当前群组不在白名单中"

        # 3. 解析命令获取基础命令
        base_command = self._extract_base_command(command)
        if not base_command:
            return False, "无法解析命令"

        # 4. 检查基础命令是否在白名单中
        if base_command not in self.config.allowed_commands:
            return False, f"命令 '{base_command}' 不在白名单中"

        # 5. 检查是否匹配危险模式
        for pattern in self.blocked_patterns_compiled:
            if pattern.search(command):
                return False, f"命令包含被阻止的危险模式: {pattern.pattern}"

        return True, "命令验证通过"

    def check_dangerous_command(self, command: str) -> tuple[bool, str | None]:
        """
        检查是否为危险命令
        
        Returns:
            (是否为危险命令, 警告信息)
        """
        for dangerous_cmd in self.config.dangerous_commands:
            pattern = dangerous_cmd.get("pattern", "")
            warning = dangerous_cmd.get("warning", "")

            if re.match(pattern, command, re.IGNORECASE):
                return True, warning

        return False, None

    def _extract_base_command(self, command: str) -> str | None:
        """提取命令的基础命令名"""
        try:
            # 使用 shlex 安全地解析命令
            parts = shlex.split(command)
            if not parts:
                return None

            base_cmd = parts[0]

            # 处理可能的路径（如 /bin/ls -> ls）
            base_cmd = base_cmd.split("/")[-1]

            return base_cmd

        except Exception as e:
            logger.error(f"解析命令失败: {e}")
            return None

    def sanitize_command(self, command: str) -> str:
        """清理命令字符串"""
        # 移除可能的危险字符
        # 这里主要依赖白名单机制，此函数用于额外的清理

        # 移除控制字符
        command = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", command)

        # 移除多个连续空格
        command = re.sub(r"\s+", " ", command)

        # 移除首尾空格
        command = command.strip()

        return command

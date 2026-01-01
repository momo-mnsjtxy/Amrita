"""Linux命令执行插件配置"""

from typing import Any

from pydantic import BaseModel, Field


class LinuxCmdConfig(BaseModel):
    """Linux命令执行配置"""

    enabled: bool = Field(default=False, description="是否启用Linux命令执行功能")

    require_permission: str = Field(
        default="linuxcmd.exec",
        description="执行命令所需的权限节点"
    )

    allowed_commands: list[str] = Field(
        default_factory=lambda: [
            "ls", "pwd", "whoami", "date", "uname", "free", "df",
            "uptime", "top", "ps", "netstat", "ss", "ping", "curl"
        ],
        description="允许执行的命令列表（白名单）"
    )

    blocked_patterns: list[str] = Field(
        default_factory=lambda: [
            r"rm.*-rf.*(/|\*)", r".*\|\s*sh", r".*\|\s*b ash", r"wget.*\|", r"curl.*\|",
            r".*>/dev/sd", r".*mkfs", r".*dd.*if=", r".*:(){.*:|:&};:",
            "/etc/passwd", "/etc/shadow", "/proc", "/sys"
        ],
        description="阻止的命令模式（正则表达式）"
    )

    max_execution_time: int = Field(
        default=30,
        description="命令最大执行时间（秒）",
        ge=1,
        le=300
    )

    max_output_size: int = Field(
        default=4096,
        description="命令输出最大字节数",
        ge=512,
        le=16384
    )

    require_confirmation: bool = Field(
        default=True,
        description="执行危险命令时是否需要确认"
    )

    allowed_users: list[str] = Field(
        default_factory=list,
        description="允许执行命令的用户ID列表（空列表表示不限制）"
    )

    allowed_groups: list[str] = Field(
        default_factory=list,
        description="允许执行命令的群组ID列表（空列表表示不限制）"
    )

    log_commands: bool = Field(
        default=True,
        description="是否记录执行的命令到日志"
    )

    dangerous_commands: list[dict[str, Any]] = Field(
        default_factory=lambda: [
            {"pattern": "^rm", "warning": "删除命令可能会导致数据丢失"},
            {"pattern": "^chmod", "warning": "权限修改可能影响系统安全"},
            {"pattern": "^chown", "warning": "所有者修改可能影响系统安全"},
            {"pattern": "^kill", "warning": "终止进程可能影响系统运行"},
            {"pattern": "^reboot", "warning": "重启命令将重启整个系统"},
            {"pattern": "^shutdown", "warning": "关机命令将关闭整个系统"},
            {"pattern": "^systemctl", "warning": "服务管理命令可能影响系统服务"}
        ],
        description="危险命令列表及警告信息"
    )

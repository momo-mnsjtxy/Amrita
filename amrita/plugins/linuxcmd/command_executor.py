"""Linux命令执行器"""

import asyncio
import subprocess

from nonebot import logger, on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event
from nonebot.params import CommandArg

from amrita.plugins.perm.command_manager import (
    local_manager as permission_manager,  # type: ignore
)

from .config import LinuxCmdConfig
from .security import CommandSecurity

# 加载配置
linux_config = LinuxCmdConfig()
security_validator = CommandSecurity(linux_config)

# 创建命令执行器
cmd_executor = on_command(
    "cmd",
    aliases={"命令", "执行"},
    priority=5,
    block=True
)

class CommandExecutor:
    """命令执行器"""

    def __init__(self, config: LinuxCmdConfig):
        self.config = config

    async def execute_command(
        self,
        command: str,
        max_execution_time: int | None = None
    ) -> tuple[str, int]:
        """
        执行命令并返回结果

        Args:
            command: 要执行的命令
            max_execution_time: 最大执行时间

        Returns:
            (输出结果, 返回码)
        """
        if max_execution_time is None:
            max_execution_time = self.config.max_execution_time

        try:
            # 使用 subprocess 执行命令
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )

            # 等待命令完成，但设置超时
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=max_execution_time
                )

                # 合并标准输出和错误输出
                output = stdout.decode("utf-8", errors="ignore")
                error_output = stderr.decode("utf-8", errors="ignore")

                if error_output:
                    output += f"\n错误输出:\n{error_output}"

                return_code = process.returncode if process.returncode is not None else -1
                return output, return_code

            except asyncio.TimeoutError:
                # 超时，终止进程
                process.kill()
                await process.wait()

                return f"命令执行超时（超过 {max_execution_time} 秒）", -1

        except Exception as e:
            logger.error(f"执行命令失败: {e}")
            return f"命令执行失败: {e!s}", -1

    def truncate_output(self, output: str) -> str:
        """截断输出以符合长度限制"""

        if len(output.encode("utf-8")) <= self.config.max_output_size:
            return output

        # 计算截断长度
        max_chars = self.config.max_output_size // 4  # 假设平均每个字符4字节

        if max_chars < len(output):
            truncated = output[:max_chars]
            truncated += f"\n...（输出过长，已截断，显示前 {max_chars} 个字符）"
            return truncated

        return output


# 命令执行处理器
@cmd_executor.handle()
async def handle_command(event: Event, args: Message = CommandArg()):
    """处理命令执行请求"""

    if not linux_config.enabled:
        await cmd_executor.finish("Linux命令执行功能已禁用")
        return

    # 获取用户ID和群组ID
    user_id = str(getattr(event, "user_id", ""))
    group_id = str(getattr(event, "group_id", ""))

    # 权限检查
    required_perm = getattr(linux_config, "require_permission", "linuxcmd.exec")
    if not await permission_manager.require_permission(event, required_perm):
        await cmd_executor.finish(f"您没有执行Linux命令的权限（需要权限: {required_perm}）")
        return

    # 获取命令
    command = args.extract_plain_text().strip()
    if not command:
        await cmd_executor.finish(
            "请提供要执行的命令，例如：\n"
            "/cmd ls -la\n"
            "/cmd pwd\n"
            "/cmd whoami"
        )
        return

    # 清理命令
    command = security_validator.sanitize_command(command)

    # 验证命令安全性
    is_valid, reason = security_validator.validate_command(command, user_id, group_id)
    if not is_valid:
        await cmd_executor.finish(f"命令被拒绝: {reason}")
        return

    # 检查是否为危险命令
    is_dangerous, warning = security_validator.check_dangerous_command(command)
    if is_dangerous and linux_config.require_confirmation:
        await cmd_executor.send(f"⚠️ 警告：{warning}\n请再次确认是否执行：{command}")
        return

    # 记录命令日志
    if linux_config.log_commands:
        logger.info(f"用户 {user_id} 执行命令: {command}")

    # 执行命令
    await cmd_executor.send(f"🖥️ 正在执行命令: {command}")

    executor = CommandExecutor(linux_config)
    output, returncode = await executor.execute_command(command)

    if output:
        output = executor.truncate_output(output)

    # 构建回复
    if returncode == 0:
        reply = f"✅ 命令执行成功 (返回码: {returncode})\n"
        reply += f"```\n{output}\n```" if output else "(无输出)"
    else:
        reply = f"❌ 命令执行失败 (返回码: {returncode})\n"
        if output:
            reply += f"```\n{output}\n```"
        else:
            reply += "无输出信息"

    await cmd_executor.finish(reply)


# 创建命令帮助
@cmd_executor.handle()
async def handle_command_help(event: Event, args: Message = CommandArg()):
    """显示命令帮助"""
    if args.extract_plain_text().strip() == "help":
        help_text = "🔧 Linux命令执行插件帮助\n\n"
        help_text += "使用方法：\n"
        help_text += "/cmd <命令> - 执行Linux命令\n\n"

        help_text += "可用命令（白名单）：\n"
        for cmd in linux_config.allowed_commands:
            help_text += f"  • {cmd}\n"

        help_text += "\n安全提示：\n"
        help_text += "• 所有命令都经过安全检查\n"
        help_text += "• 危险命令需要额外确认\n"
        help_text += "• 命令执行有时间限制\n"
        help_text += "• 输出过长会被自动截断"

        await cmd_executor.finish(help_text)

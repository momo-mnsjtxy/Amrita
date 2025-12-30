import sys
from asyncio import subprocess

from aiohttp import ClientSession, ClientTimeout
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from packaging import version

from amrita.cli import IS_IN_VENV
from amrita.plugins.perm.API.admin import is_lp_admin
from amrita.utils.utils import get_amrita_version

amrita = on_command(
    "miniagent",
    aliases={"MiniAgent", "amrita", "Amrita"},
    priority=10,
    block=True,
    permission=is_lp_admin,
)


@amrita.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    arg_list = args.extract_plain_text().strip().split()
    match len(arg_list):
        case 1:
            if arg_list[0] == "version":
                await matcher.finish(
                    f"MiniAgent v{get_amrita_version()} (based on Amrita)"
                )

            if arg_list[0] == "update":
                await matcher.send("正在检查 MiniAgent 更新...")

                try:
                    timeout = ClientTimeout(total=10)
                    async with ClientSession(timeout=timeout) as session:
                        metadata = None
                        package_name = None
                        for candidate in (
                            "minichatagent",
                            "miniagent",
                            "amrita",
                        ):
                            async with session.get(
                                f"https://pypi.org/pypi/{candidate}/json"
                            ) as response:
                                if response.status != 200:
                                    continue
                                metadata = await response.json()
                                package_name = candidate
                                break

                    if not package_name or not metadata or metadata.get("releases") == {}:
                        await matcher.send("检查更新失败，请稍后再试")
                        return

                    latest_version = max(metadata["releases"].keys(), key=version.parse)

                except Exception:
                    await matcher.finish("错误：无法检查更新")
                else:
                    if version.parse(latest_version) > version.parse(get_amrita_version()):
                        await matcher.send(
                            f"新版本已就绪: {latest_version}，正在更新..."
                        )
                        try:
                            install_cmd = (
                                f"uv add {package_name}=={latest_version}"
                                if IS_IN_VENV
                                else (
                                    f"pip install {package_name}=={latest_version}"
                                    + (
                                        " --break-system-packages"
                                        if sys.platform.lower() == "linux"
                                        else ""
                                    )
                                )
                            )
                            await (
                                await subprocess.create_subprocess_shell(install_cmd)
                            ).wait()
                            await matcher.send("完成更新，请重新启动程序以应用更改。")
                        except Exception as e:
                            await matcher.send("更新失败：" + str(e))
                    else:
                        await matcher.send("已是最新版本。")
                return

            await matcher.finish("错误：参数错误")

        case _:
            await matcher.finish(
                "错误：需要1个参数！\n输入格式：/miniagent [参数]\n可用：version|update\n别名：/amrita"
            )

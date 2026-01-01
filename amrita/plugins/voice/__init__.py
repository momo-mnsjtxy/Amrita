from nonebot.plugin import PluginMetadata, require

require("amrita.plugins.perm")
require("amrita.plugins.menu")

from . import (
    config,
    stt,
    tts,
    voice_processor,
)

__all__ = [
    "config",
    "stt",
    "tts",
    "voice_processor",
]

__plugin_meta__ = PluginMetadata(
    name="语音处理插件",
    description="提供语音转文字(STT)和文字转语音(TTS)功能",
    usage="支持语音消息识别和文本朗读",
    type="application",
)

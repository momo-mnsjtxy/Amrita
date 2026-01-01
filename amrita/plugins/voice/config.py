"""语音处理插件配置"""

from typing import Literal

from pydantic import BaseModel, Field


class VoiceConfig(BaseModel):
    """语音处理配置"""

    enabled: bool = Field(default=False, description="是否启用语音处理功能")

    # STT (Speech-to-Text) 配置
    stt_enabled: bool = Field(default=True, description="是否启用语音转文字功能")

    stt_provider: Literal["whisper", "baidu", "tencent", "aliyun"] = Field(
        default="whisper",
        description="STT服务提供商"
    )

    stt_api_key: str | None = Field(
        default=None,
        description="STT API密钥"
    )

    stt_api_secret: str | None = Field(
        default=None,
        description="STT API密钥（如果需要）"
    )

    stt_model: str = Field(
        default="whisper-1",
        description="STT模型名称"
    )

    stt_language: str = Field(
        default="auto",
        description="语音识别语言（auto为自动检测）"
    )

    max_audio_duration: int = Field(
        default=60,
        description="最大音频时长（秒）",
        ge=10,
        le=300
    )

    max_recognition_time: int = Field(
        default=30,
        description="语音识别超时时间（秒）",
        ge=10,
        le=60
    )

    # TTS (Text-to-Speech) 配置
    tts_enabled: bool = Field(default=True, description="是否启用文字转语音功能")

    tts_provider: Literal["openai", "baidu", "tencent", "edge"] = Field(
        default="openai",
        description="TTS服务提供商"
    )

    tts_api_key: str | None = Field(
        default=None,
        description="TTS API密钥"
    )

    tts_model: str = Field(
        default="tts-1",
        description="TTS模型名称"
    )

    tts_voice: str = Field(
        default="alloy",
        description="TTS声音类型"
    )

    tts_speed: float = Field(
        default=1.0,
        description="语音速度倍率",
        ge=0.5,
        le=2.0
    )

    max_tts_length: int = Field(
        default=1000,
        description="TTS文本最大长度（字符数）",
        ge=100,
        le=2000
    )

    # 文件存储配置
    voice_file_format: Literal["mp3", "wav", "ogg"] = Field(
        default="mp3",
        description="语音文件格式"
    )

    auto_delete_duration: int = Field(
        default=3600,
        description="语音文件自动删除时间（秒）",
        ge=60,
        le=86400
    )

    require_permission: str = Field(
        default="voice.use",
        description="使用语音功能所需的权限节点"
    )

    audio_processing_max_size: int = Field(
        default=10485760,
        description="最大音频文件大小（字节）",
        ge=1048576,
        le=104857600
    )

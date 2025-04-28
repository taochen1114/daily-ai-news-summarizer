"""
TTS服务工厂，提供不同TTS提供商的接口
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TTS_PROVIDER

from .elevenlabs_tts import ElevenLabsTTS
from .google_tts import GoogleTTS


def create_tts_service():
    """
    创建TTS服务实例
    """
    provider = TTS_PROVIDER.lower()
    
    if provider == "elevenlabs":
        return ElevenLabsTTS()
    elif provider == "google":
        return GoogleTTS()
    else:
        raise ValueError(f"不支持的TTS提供商: {provider}") 
"""
使用ElevenLabs API进行文本到语音转换
"""
import os
import time
from elevenlabs import generate, save, set_api_key, voices

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ELEVENLABS_API_KEY, AUDIO_DIR


class ElevenLabsTTS:
    """ElevenLabs TTS服务"""
    
    def __init__(self, voice_name="Rachel"):
        # 设置API密钥
        set_api_key(ELEVENLABS_API_KEY)
        
        # 获取可用声音
        self.available_voices = voices()
        self.voice_name = voice_name
        self.voice = next((v for v in self.available_voices if v.name == voice_name), None)
        
        # 如果指定的声音不存在，使用第一个可用声音
        if self.voice is None and self.available_voices:
            self.voice = self.available_voices[0]
            self.voice_name = self.voice.name
    
    def text_to_speech(self, text, output_path=None, article_id=None):
        """
        将文本转换为语音
        
        Args:
            text (str): 要转换的文本
            output_path (str, optional): 输出文件路径
            article_id (str, optional): 文章ID，用于生成文件名
            
        Returns:
            str: 生成的音频文件路径
        """
        if not text:
            raise ValueError("文本内容不能为空")
            
        # 如果未指定输出路径，使用默认路径
        if output_path is None:
            # 确保目录存在
            os.makedirs(AUDIO_DIR, exist_ok=True)
            
            # 生成文件名
            filename = f"{article_id or int(time.time())}.mp3"
            output_path = os.path.join(AUDIO_DIR, filename)
        
        try:
            # 生成音频
            audio = generate(
                text=text,
                voice=self.voice_name,
                model="eleven_multilingual_v2"
            )
            
            # 保存音频文件
            save(audio, output_path)
            
            print(f"已生成音频文件: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"音频生成失败: {e}")
            raise 
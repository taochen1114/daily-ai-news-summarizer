"""
使用OpenAI Whisper API进行文本到语音转换
"""
import os
import time
from openai import OpenAI

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, AUDIO_DIR


class WhisperTTS:
    """OpenAI Whisper TTS服务"""
    
    def __init__(self, model="tts-1", voice="alloy"):
        # 设置API密钥
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.voice = voice
    
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
            response = self.client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text
            )
            
            # 保存音频文件
            response.stream_to_file(output_path)
            
            print(f"已生成音频文件: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"音频生成失败: {e}")
            raise 
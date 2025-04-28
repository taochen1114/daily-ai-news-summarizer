"""
使用Google Text-to-Speech API进行文本到语音转换
"""
import os
import time
from google.cloud import texttospeech

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_APPLICATION_CREDENTIALS, AUDIO_DIR


class GoogleTTS:
    """Google TTS服务"""
    
    def __init__(self, language_code="zh-CN", voice_name="zh-CN-Standard-A"):
        # 设置环境变量以使用Google凭证
        if GOOGLE_APPLICATION_CREDENTIALS:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
            
        self.client = texttospeech.TextToSpeechClient()
        self.language_code = language_code
        self.voice_name = voice_name
        
        # 音频配置
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
    
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
            # 设置输入文本
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # 设置语音
            voice = texttospeech.VoiceSelectionParams(
                language_code=self.language_code,
                name=self.voice_name
            )
            
            # 请求TTS API
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=self.audio_config
            )
            
            # 将响应内容写入文件
            with open(output_path, "wb") as out:
                out.write(response.audio_content)
                
            print(f"已生成音频文件: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"音频生成失败: {e}")
            raise 
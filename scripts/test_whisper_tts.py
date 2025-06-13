#!/usr/bin/env python
"""
测试 Whisper TTS 功能
"""
import os
from dotenv import load_dotenv
from audio.whisper_tts import WhisperTTS

# 加载环境变量
load_dotenv()

def test_whisper_tts():
    """测试 Whisper TTS 功能"""
    print("开始测试 Whisper TTS...")
    
    # 创建 WhisperTTS 实例
    tts = WhisperTTS()
    
    # 测试文本
    test_text = "这是一个测试文本，用于验证 Whisper TTS 功能是否正常工作。"
    
    try:
        # 生成音频
        output_path = tts.text_to_speech(
            text=test_text,
            article_id="test_whisper"
        )
        
        print(f"测试成功！音频文件已生成：{output_path}")
        print(f"文件大小：{os.path.getsize(output_path) / 1024:.2f} KB")
        
    except Exception as e:
        print(f"测试失败：{e}")

if __name__ == "__main__":
    test_whisper_tts() 
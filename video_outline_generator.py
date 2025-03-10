import os
import moviepy.editor as mp
import speech_recognition as sr
import requests
import json
import time
from typing import List, Dict
from vosk import Model, KaldiRecognizer
import wave

class VideoOutlineGenerator:
    def __init__(self, api_key: str):
        """初始化视频大纲生成器
        Args:
            api_key: DeepSeek API密钥
        """
        self.recognizer = sr.Recognizer()
        self.api_key = api_key
        # 初始化Vosk模型
        model_path = os.path.expanduser('~/.cache/vosk')
        model_name = 'vosk-model-cn-0.22'
        model_full_path = os.path.join(model_path, model_name)

        # 检查模型是否存在
        if not os.path.exists(model_full_path):
            print(f"未找到Vosk中文模型：{model_full_path}")
            print("将使用在线语音识别服务作为备选方案")
            self.vosk_recognizer = None
            return

        try:
            model = Model(model_path=model_full_path)
            self.vosk_recognizer = KaldiRecognizer(model, 16000)
        except Exception as e:
            print(f"初始化Vosk模型时出错：{e}")
            print("将使用在线语音识别服务作为备选方案")
            self.vosk_recognizer = None

    def extract_audio(self, video_path: str, output_path: str) -> str:
        """从视频中提取音频
        Args:
            video_path: 视频文件路径
            output_path: 音频输出路径
        Returns:
            输出的音频文件路径
        """
        video = mp.VideoFileClip(video_path)
        audio = video.audio
        # 设置音频参数以确保与语音识别服务兼容
        # MoviePy的AudioFileClip没有set_nchannels方法，直接在write_audiofile中设置参数
        audio.write_audiofile(output_path, fps=16000, nbytes=2, codec='pcm_s16le', ffmpeg_params=['-ac', '1'])  # 16位PCM编码，单声道
        return output_path

    def transcribe_audio(self, audio_path: str, max_retries: int = 3, retry_delay: int = 5) -> str:
        """将音频转换为文本
        Args:
            audio_path: 音频文件路径
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
        Returns:
            转换后的文本内容
        """
        try:
            # 首先尝试使用Vosk进行离线识别
            with wave.open(audio_path, 'rb') as wf:
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != 'NONE':
                    print("音频格式不兼容，尝试使用在线服务")
                else:
                    while True:
                        data = wf.readframes(4000)
                        if len(data) == 0:
                            break
                        if self.vosk_recognizer.AcceptWaveform(data):
                            continue
                    result = json.loads(self.vosk_recognizer.FinalResult())
                    if result.get('text'):
                        return result['text']

            # 如果Vosk识别失败，使用Google在线服务作为备选
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
                
                for attempt in range(max_retries):
                    try:
                        text = self.recognizer.recognize_google(audio, language='zh-CN')
                        return text
                    except sr.UnknownValueError:
                        print("无法识别音频内容")
                        return ""
                    except sr.RequestError as e:
                        if attempt < max_retries - 1:
                            print(f"语音识别服务连接失败（尝试 {attempt + 1}/{max_retries}）：{e}")
                            time.sleep(retry_delay)
                            continue
                        else:
                            print(f"语音识别服务连接失败，已达到最大重试次数：{e}")
                            return ""
        except Exception as e:
            print(f"音频转换过程出现错误：{e}")
            return ""

    def generate_outline(self, text: str) -> str:
        """使用DeepSeek生成文本大纲
        Args:
            text: 需要生成大纲的文本内容
        Returns:
            大纲内容字符串
        """
        prompt = f"请为以下内容生成一个结构化的大纲：\n{text}"
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-r1:32b",
                "prompt": prompt
            },
            stream=True
        )
        
        if response.status_code == 200:
            try:
                content = ''
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        content += data.get('response', '')
                return content.strip()
            except Exception as e:
                print(f"处理流式响应时出错: {e}")
                return ""
        else:
            print(f"请求DeepSeek API失败：{response.status_code}")
            return ""

    def process_video(self, video_path: str) -> str:
        """处理视频并生成大纲
        Args:
            video_path: 视频文件路径
        Returns:
            生成的大纲内容
        """
        # 生成临时音频文件路径
        audio_path = os.path.splitext(video_path)[0] + ".wav"
        
        try:
            # 提取音频
            self.extract_audio(video_path, audio_path)
            
            # 转换音频到文本
            text = self.transcribe_audio(audio_path)
            
            # 生成大纲
            if text:
                outline = self.generate_outline(text)
                return outline
            else:
                return ""
        finally:
            # 清理临时文件
            if os.path.exists(audio_path):
                os.remove(audio_path)

def main():
    # 使用示例
    api_key = "your-api-key"
    video_path = "/Users/bati/Downloads/zhouyue.mp4"
    
    generator = VideoOutlineGenerator(api_key)
    outline = generator.process_video(video_path)
    print("视频大纲：")
    print(outline)

if __name__ == "__main__":
    main()
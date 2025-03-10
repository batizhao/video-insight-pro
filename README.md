# Video Insight Pro

Video Insight Pro 是一个强大的视频内容分析工具，能够自动从视频中提取音频内容，将语音转换为文本，并生成结构化的内容大纲。

## 功能特点

- 视频音频提取：自动从视频文件中提取音频内容
- 语音识别：支持中文语音识别，采用双重识别方案
  - 离线识别：使用 Vosk 模型进行本地语音识别
  - 在线识别：当离线识别不可用时，自动切换到 Google 语音识别服务
- 智能大纲生成：使用 DeepSeek API 自动生成结构化的内容大纲

## 系统要求

- Python 3.7+
- FFmpeg（用于音频处理）
- 足够的磁盘空间用于存储临时音频文件

## 安装说明

1. 克隆仓库：

```bash
git clone https://github.com/batizhao/video-insight-pro.git
cd video-insight-pro
```

2. 安装依赖：

```bash
pip install moviepy SpeechRecognition vosk requests
```

3. 下载 Vosk 中文模型：

模型将自动下载到 `~/.cache/vosk/vosk-model-cn-0.22` 目录下。如果需要手动下载，请访问 [Vosk 模型下载页面](https://alphacephei.com/vosk/models)。

## 配置

1. 获取 DeepSeek API 密钥
2. 将 API 密钥配置到程序中

## 使用方法

```python
from video_outline_generator import VideoOutlineGenerator

# 初始化生成器
generator = VideoOutlineGenerator(api_key="your-api-key")

# 处理视频文件
outline = generator.process_video("/path/to/your/video.mp4")

# 打印生成的大纲
print(outline)
```

## 示例输出

```
视频大纲：
1. 主题概述
   1.1 背景介绍
   1.2 核心观点
2. 详细内容
   2.1 要点一
   2.2 要点二
   ...
```

## 注意事项

- 确保系统已正确安装 FFmpeg
- 视频文件应具有清晰的音频轨道
- 建议使用高质量的视频源以获得更好的识别效果
- 处理大型视频文件时可能需要较长时间

## 许可证

[Apache License 2.0](LICENSE)

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 作者

[@batizhao]

## 致谢

- [MoviePy](https://zulko.github.io/moviepy/)
- [Vosk](https://alphacephei.com/vosk/)
- [DeepSeek](https://deepseek.com/)
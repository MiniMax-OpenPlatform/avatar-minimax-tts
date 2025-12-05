#!/bin/bash

# HeyGem Digital Human Docker运行脚本
#
# 使用方法:
#   ./run_docker.sh                           # 使用默认示例文件运行
#   ./run_docker.sh audio.wav video.mp4       # 使用自定义文件运行

AUDIO_FILE=${1:-"example/audio.wav"}
VIDEO_FILE=${2:-"example/video.mp4"}

# 获取当前目录的绝对路径
WORK_DIR=$(pwd)

echo "======================================"
echo "HeyGem Digital Human - Docker版本"
echo "======================================"
echo "音频文件: ${AUDIO_FILE}"
echo "视频文件: ${VIDEO_FILE}"
echo "工作目录: ${WORK_DIR}"
echo "======================================"

# 运行Docker容器
sudo docker run --rm \
  --gpus all \
  -v "${WORK_DIR}":/workspace \
  -w /workspace \
  heygem-digital-human:latest \
  /usr/local/python38/bin/python3.8 run.py \
    --audio_path "${AUDIO_FILE}" \
    --video_path "${VIDEO_FILE}"

echo "======================================"
echo "处理完成！输出文件在 ./result/ 目录中"
echo "======================================"

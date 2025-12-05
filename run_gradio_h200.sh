#!/bin/bash

# HeyGem Digital Human - H200 GPU兼容启动脚本
# 使用环境变量尝试绕过CUDA sm_90兼容性问题

echo "======================================"
echo "HeyGem Digital Human - H200 GPU模式"
echo "======================================"

sudo docker run --rm \
  --gpus all \
  -v "$(pwd)":/workspace \
  -w /workspace \
  -p 7860:7860 \
  -e CUDA_LAUNCH_BLOCKING=1 \
  -e TORCH_CUDA_ARCH_LIST="8.0;8.6;9.0" \
  -e CUDA_FORCE_PTX_JIT=1 \
  -e PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512" \
  heygem-digital-human:latest \
  /usr/local/python38/bin/python3.8 app.py

echo "======================================"
echo "服务已停止"
echo "======================================"

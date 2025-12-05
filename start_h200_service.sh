#!/bin/bash

# HeyGem数字人服务 - H200 GPU启动脚本
# 使用PyTorch 2.0.0+cu118修复版本

echo "======================================"
echo "启动HeyGem数字人服务 (H200 GPU)"
echo "======================================"

sudo docker run --rm --gpus all \
  -v "$(pwd)":/workspace \
  -w /workspace \
  -p 7860:7860 \
  -e http_proxy=http://pac-internal.xaminim.com:3129 \
  -e https_proxy=http://pac-internal.xaminim.com:3129 \
  heygem-digital-human:latest \
  /bin/bash -c '
    echo "步骤1: 升级PyTorch到2.0.0+cu118 (H200兼容)..."
    pip uninstall -y torch torchvision torchaudio triton 2>/dev/null || true

    pip install torch==2.0.0+cu118 torchvision==0.15.0+cu118 torchaudio==2.0.0+cu118 \
        --index-url https://download.pytorch.org/whl/cu118 \
        --no-deps >/dev/null 2>&1

    pip install filelock typing-extensions sympy networkx jinja2 numpy pillow requests >/dev/null 2>&1

    echo "✓ PyTorch 2.0.0+cu118 已安装"
    echo ""
    echo "步骤2: 启动Gradio服务 (queue=False禁用流式传输)..."
    /usr/local/python38/bin/python3.8 app.py
  '

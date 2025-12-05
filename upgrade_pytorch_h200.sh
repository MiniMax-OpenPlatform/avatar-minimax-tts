#!/bin/bash

# 在容器内升级PyTorch以支持H200
# 警告：这会修改.so文件的依赖，可能导致崩溃

echo "======================================"
echo "升级PyTorch到2.1.0以支持H200 GPU"
echo "警告：这可能破坏.so文件兼容性"
echo "======================================"

sudo docker run --rm --gpus all \
  -v "$(pwd)":/workspace \
  -w /workspace \
  -p 7860:7860 \
  -e http_proxy=http://pac-internal.xaminim.com:3129 \
  -e https_proxy=http://pac-internal.xaminim.com:3129 \
  heygem-digital-human:latest \
  /bin/bash -c "
    echo '步骤1: 卸载旧版PyTorch...'
    pip uninstall -y torch torchvision torchaudio

    echo '步骤2: 安装PyTorch 2.0.0 (CUDA 11.8, 可能部分支持H200)...'
    pip install torch==2.0.0 torchvision==0.15.0 torchaudio==2.0.0 --index-url https://download.pytorch.org/whl/cu118

    echo '步骤3: 升级transformers以兼容PyTorch 2.1...'
    pip uninstall -y transformers
    pip install transformers==4.30.0 --no-deps
    pip install tokenizers regex sacremoses

    echo '步骤4: 测试CUDA可用性...'
    python3.8 -c 'import torch; print(f\"PyTorch版本: {torch.__version__}\"); print(f\"CUDA可用: {torch.cuda.is_available()}\"); print(f\"GPU数量: {torch.cuda.device_count()}\"); print(f\"GPU名称: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"无\"}')'

    echo '步骤5: 启动Gradio服务...'
    /usr/local/python38/bin/python3.8 app.py
  "

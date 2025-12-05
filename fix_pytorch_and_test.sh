#!/bin/bash

# 修复PyTorch 2.0安装并测试H200服务

echo "======================================"
echo "选项B：修复PyTorch 2.0安装"
echo "======================================"

sudo docker run --rm --gpus all \
  -v "$(pwd)":/workspace \
  -w /workspace \
  -p 7860:7860 \
  -e http_proxy=http://pac-internal.xaminim.com:3129 \
  -e https_proxy=http://pac-internal.xaminim.com:3129 \
  heygem-digital-human:latest \
  /bin/bash -c '
    echo "步骤1: 检查PyTorch是否已安装..."
    python3.8 -c "import torch; print(f\"当前PyTorch版本: {torch.__version__}\")" 2>&1 || echo "PyTorch未安装或损坏"

    echo ""
    echo "步骤2: 如果PyTorch未正确安装，重新安装（跳过triton）..."
    pip uninstall -y torch torchvision torchaudio triton 2>/dev/null || true

    # 安装PyTorch 2.0.0但跳过triton依赖（H200可能不需要triton）
    pip install torch==2.0.0+cu118 torchvision==0.15.0+cu118 torchaudio==2.0.0+cu118 \
        --index-url https://download.pytorch.org/whl/cu118 \
        --no-deps

    # 手动安装PyTorch的核心依赖
    pip install filelock typing-extensions sympy networkx jinja2 numpy pillow requests

    echo ""
    echo "步骤3: 验证PyTorch安装..."
    python3.8 -c "
import torch
print(f\"✓ PyTorch版本: {torch.__version__}\")
print(f\"✓ CUDA是否可用: {torch.cuda.is_available()}\")
if torch.cuda.is_available():
    print(f\"✓ GPU数量: {torch.cuda.device_count()}\")
    for i in range(torch.cuda.device_count()):
        print(f\"  GPU {i}: {torch.cuda.get_device_name(i)}\")
        print(f\"  计算能力: sm_{torch.cuda.get_device_capability(i)[0]}{torch.cuda.get_device_capability(i)[1]}\")
else:
    print(\"✗ CUDA不可用\")
" || echo "PyTorch测试失败"

    echo ""
    echo "步骤4: 测试加载.so文件兼容性..."
    python3.8 -c "
import sys
sys.path.insert(0, \"/workspace\")
try:
    import service.trans_dh_service
    print(\"✓ trans_dh_service.so 加载成功\")
except Exception as e:
    print(f\"✗ trans_dh_service.so 加载失败: {e}\")
    import traceback
    traceback.print_exc()
" 2>&1

    echo ""
    echo "步骤5: 启动Gradio服务测试..."
    echo "按Ctrl+C可以停止服务"
    echo ""

    /usr/local/python38/bin/python3.8 app.py
  '

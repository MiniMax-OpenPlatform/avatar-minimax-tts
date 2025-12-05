#!/bin/bash

# HeyGem数字人服务 - H200 GPU持久化启动脚本
# 使用-d参数在后台运行，不依赖终端会话

echo "======================================"
echo "启动HeyGem数字人服务 (H200 GPU - 守护进程模式)"
echo "======================================"

# 检查是否已有运行的容器
if sudo docker ps | grep -q heygem-digital-human; then
    echo "⚠️  检测到已有服务在运行"
    sudo docker ps | grep heygem-digital-human
    read -p "是否停止现有服务并重启？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "停止现有服务..."
        sudo docker stop $(sudo docker ps -q --filter ancestor=heygem-digital-human:latest)
    else
        echo "保持现有服务运行，退出。"
        exit 0
    fi
fi

echo ""
echo "启动新服务..."

# 使用-d参数让容器在后台运行
# 移除--rm，使用--restart unless-stopped实现自动重启
sudo docker run -d \
  --name heygem-service \
  --restart unless-stopped \
  --gpus all \
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

echo ""
echo "======================================"
echo "✓ 服务已启动 (守护进程模式)"
echo "======================================"
echo ""
echo "容器信息:"
sudo docker ps | grep heygem-service
echo ""
echo "访问地址: http://localhost:7860"
echo ""
echo "常用命令:"
echo "  查看日志: sudo docker logs -f heygem-service"
echo "  停止服务: sudo docker stop heygem-service"
echo "  重启服务: sudo docker restart heygem-service"
echo "  删除容器: sudo docker rm -f heygem-service"
echo ""

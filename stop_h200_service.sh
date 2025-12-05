#!/bin/bash

# 停止HeyGem数字人服务

echo "======================================"
echo "停止HeyGem数字人服务"
echo "======================================"

# 查找所有heygem相关的容器
CONTAINERS=$(sudo docker ps -q --filter ancestor=heygem-digital-human:latest)

if [ -z "$CONTAINERS" ]; then
    echo "❌ 没有找到正在运行的HeyGem服务"
    exit 0
fi

echo "找到以下运行中的容器:"
sudo docker ps | grep heygem-digital-human

echo ""
read -p "确认停止所有HeyGem服务？(y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "正在停止服务..."
    sudo docker stop $CONTAINERS
    echo "✓ 服务已停止"

    # 如果有命名容器，也删除
    if sudo docker ps -a | grep -q heygem-service; then
        sudo docker rm heygem-service 2>/dev/null
        echo "✓ 容器已清理"
    fi
else
    echo "已取消操作"
fi

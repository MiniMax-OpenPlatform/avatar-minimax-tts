#!/bin/bash

# 测试可配置质量版本的数字人服务

echo "======================================"
echo "测试可配置质量的HeyGem服务 (端口7861)"
echo "======================================"

# 检查原服务是否在运行
if sudo docker ps | grep -q heygem-service; then
    echo "✓ 原服务 (端口7860) 仍在运行"
    echo "✓ 测试服务将使用端口7861"
else
    echo "⚠️  原服务未运行，建议先启动: bash start_h200_daemon.sh"
fi

echo ""
echo "启动测试服务..."

# 在现有容器中运行测试版本
sudo docker exec -d heygem-service /bin/bash -c '
    echo "启动可配置质量版本..."
    cd /workspace
    nohup /usr/local/python38/bin/python3.8 app_configurable.py > configurable.log 2>&1 &
    echo "✓ 测试服务已启动"
'

sleep 5

echo ""
echo "======================================"
echo "✓ 测试服务启动完成"
echo "======================================"
echo ""
echo "访问地址:"
echo "  原版本 (固定质量): http://localhost:7860"
echo "  测试版 (可调质量): http://localhost:7861"
echo ""
echo "查看测试服务日志:"
echo "  sudo docker exec heygem-service tail -f /workspace/configurable.log"
echo ""
echo "停止测试服务:"
echo "  sudo docker exec heygem-service pkill -f app_configurable.py"
echo ""

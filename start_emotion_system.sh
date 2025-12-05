#!/bin/bash

# 启动情感驱动数字人系统

echo "======================================"
echo "🎭 情感驱动数字人系统启动"
echo "======================================"

# 检查现有服务
if sudo docker ps | grep -q heygem-service; then
    echo "✓ 基础服务已运行"
else
    echo "❌ 基础服务未运行，请先执行:"
    echo "   bash start_h200_daemon.sh"
    exit 1
fi

echo ""
echo "安装音频分析依赖库..."

# 在容器中安装librosa
sudo docker exec heygem-service /bin/bash -c '
    echo "安装音频分析库..."
    pip install librosa==0.9.2 soundfile==0.12.1 -i https://pypi.tuna.tsinghua.edu.cn/simple/ || true
    echo "✓ 音频依赖安装完成"
'

echo ""
echo "启动情感驱动系统..."

# 启动情感驱动版本
sudo docker exec -d heygem-service /bin/bash -c '
    echo "启动情感驱动数字人系统..."
    cd /workspace
    nohup /usr/local/python38/bin/python3.8 app_emotion_driven.py > emotion_system.log 2>&1 &
    echo "✓ 情感驱动系统已启动"
'

sleep 8

echo ""
echo "======================================"
echo "✅ 情感驱动系统启动完成"
echo "======================================"
echo ""
echo "可用服务:"
echo "  基础版本:     http://localhost:7860"
echo "  可调质量版:   http://localhost:7861"
echo "  🆕情感驱动版: http://localhost:7862"
echo ""
echo "使用说明:"
echo "1. 准备一段有情感变化的音频文件"
echo "2. 准备多个不同情感的视频文件:"
echo "   - 高兴视频 (文件名包含happy)"
echo "   - 悲伤视频 (文件名包含sad)"
echo "   - 兴奋视频 (文件名包含excited)"
echo "   - 平静视频 (文件名包含calm)"
echo "   - 中性视频 (文件名包含neutral)"
echo "3. 访问 http://localhost:7862 开始体验"
echo ""
echo "监控命令:"
echo "  查看日志: sudo docker exec heygem-service tail -f /workspace/emotion_system.log"
echo "  停止系统: sudo docker exec heygem-service pkill -f app_emotion_driven.py"
echo ""
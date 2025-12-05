#!/bin/bash

# 启动单视频情感增强系统

echo "======================================"
echo "🎭 单视频情感增强系统启动"
echo "======================================"

# 检查基础服务
if sudo docker ps | grep -q heygem-service; then
    echo "✓ 基础服务运行中"
else
    echo "❌ 基础服务未运行，请先启动:"
    echo "   bash start_h200_daemon.sh"
    exit 1
fi

echo ""
echo "检查并安装依赖..."

# 安装音频处理库
sudo docker exec heygem-service /bin/bash -c '
    echo "安装librosa和音频处理库..."
    pip install librosa==0.9.2 soundfile==0.12.1 -i https://pypi.tuna.tsinghua.edu.cn/simple/ --quiet
    echo "✓ 依赖安装完成"
'

echo ""
echo "启动单视频情感增强系统..."

# 启动单视频情感系统
sudo docker exec -d heygem-service /bin/bash -c '
    echo "启动单视频情感增强系统..."
    cd /workspace
    nohup /usr/local/python38/bin/python3.8 app_single_video_emotion.py > single_emotion.log 2>&1 &
    echo "✓ 单视频情感系统已启动"
'

sleep 5

echo ""
echo "======================================"
echo "✅ 单视频情感增强系统启动完成"
echo "======================================"
echo ""
echo "🌟 服务列表:"
echo "  基础版本:     http://localhost:7860"
echo "  可调质量版:   http://localhost:7861"
echo "  多视频情感版: http://localhost:7862"
echo "  🆕单视频情感版: http://localhost:7863"
echo ""
echo "🎯 单视频情感增强特色:"
echo "  ✅ 仅需1个视频 + 1个音频"
echo "  ✅ 自动情感分析 (7种情感类型)"
echo "  ✅ 3DMM参数实时调制"
echo "  ✅ 详细的情感分析报告"
echo "  ✅ 支持情感强度控制"
echo ""
echo "📝 使用建议:"
echo "  - 视频: 选择表情自然、光线良好的正面视频"
echo "  - 音频: 选择情感变化丰富的音频内容"
echo "  - 时长: 建议视频15秒以上，音频不限长度"
echo ""
echo "🔧 监控命令:"
echo "  查看日志: sudo docker exec heygem-service tail -f /workspace/single_emotion.log"
echo "  停止服务: sudo docker exec heygem-service pkill -f app_single_video_emotion.py"
echo ""
#!/bin/bash

# 启动动作增强数字人系统

echo "======================================"
echo "🎪 动作增强数字人系统启动"
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
echo "检查并安装音频分析依赖..."

# 安装librosa和音频分析库
sudo docker exec heygem-service /bin/bash -c '
    echo "安装librosa和音频分析库..."
    pip install librosa==0.9.2 soundfile==0.12.1 -i https://pypi.tuna.tsinghua.edu.cn/simple/ --quiet
    echo "✓ 音频依赖安装完成"
'

echo ""
echo "启动动作增强系统..."

# 启动动作增强版本
sudo docker exec -d heygem-service /bin/bash -c '
    echo "启动动作增强数字人系统..."
    cd /workspace
    nohup /usr/local/python38/bin/python3.8 app_motion_enhanced.py > motion_enhanced.log 2>&1 &
    echo "✓ 动作增强系统已启动"
'

sleep 6

echo ""
echo "======================================"
echo "✅ 动作增强系统启动完成"
echo "======================================"
echo ""
echo "🌟 服务列表:"
echo "  基础版本:     http://localhost:7860"
echo "  可调质量版:   http://localhost:7861"
echo "  多视频情感版: http://localhost:7862"
echo "  单视频情感版: http://localhost:7863"
echo "  🆕动作增强版: http://localhost:7864"
echo ""
echo "🎯 动作增强特色功能:"
echo "  ✅ 基于文本语义的动作识别"
echo "  ✅ 基于音频特征的动作生成"
echo "  ✅ 头部姿态实时控制 (俯仰/偏航/滚转)"
echo "  ✅ 情感-动作协同系统"
echo "  ✅ 详细的动作分析报告"
echo ""
echo "📝 支持的动作类型:"
echo "  🔄 点头: \"是的\"、\"对\"、\"没错\"、\"好的\""
echo "  🔄 摇头: \"不是\"、\"不对\"、\"错了\"、\"不行\""
echo "  🤔 歪头思考: \"思考\"、\"也许\"、\"可能\""
echo "  👀 仰望: \"希望\"、\"梦想\"、\"未来\""
echo "  ⚡ 强调: \"重要\"、\"关键\"、\"必须\""
echo ""
echo "🎵 音频特征驱动:"
echo "  - 高能量语音 → 动态头部动作"
echo "  - 低能量语音 → 微小动作"
echo "  - 音调变化大 → 表达手势"
echo ""
echo "🔧 监控命令:"
echo "  查看日志: sudo docker exec heygem-service tail -f /workspace/motion_enhanced.log"
echo "  停止服务: sudo docker exec heygem-service pkill -f app_motion_enhanced.py"
echo ""
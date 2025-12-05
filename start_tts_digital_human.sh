#!/bin/bash

# 启动TTS数字人生成系统

echo "======================================"
echo "🎤 TTS数字人生成系统启动"
echo "======================================"

# 检查基础服务
if sudo docker ps | grep -q heygem-service; then
    echo "✓ 基础容器运行中"
else
    echo "❌ 基础容器未运行，请先启动:"
    echo "   bash start_h200_daemon.sh"
    exit 1
fi

echo ""
echo "检查并安装TTS依赖..."

# 安装requests库
sudo docker exec heygem-service /bin/bash -c '
    echo "安装requests库..."
    pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple/ --quiet
    echo "✓ TTS依赖安装完成"
'

echo ""
echo "启动TTS数字人系统..."

# 启动TTS数字人版本
sudo docker exec -d heygem-service /bin/bash -c '
    echo "启动TTS数字人生成系统..."
    cd /workspace
    nohup /usr/local/python38/bin/python3.8 app_tts_digital_human.py > tts_digital_human.log 2>&1 &
    echo "✓ TTS数字人系统已启动"
'

sleep 8

echo ""
echo "======================================"
echo "✅ TTS数字人系统启动完成"
echo "======================================"
echo ""
echo "🌟 服务列表:"
echo "  基础版本:     http://localhost:7860"
echo "  可调质量版:   http://localhost:7861"
echo "  多视频情感版: http://localhost:7862"
echo "  单视频情感版: http://localhost:7863"
echo "  动作增强版:   http://localhost:7864"
echo "  🆕TTS数字人版: http://localhost:7865"
echo ""
echo "🎤 TTS数字人特色功能:"
echo "  ✅ Minimax API语音合成集成"
echo "  ✅ 文本到数字人视频一键生成"
echo "  ✅ 12种不同声音选择"
echo "  ✅ 高清语音质量 (speech-02-hd)"
echo "  ✅ 智能动作控制集成"
echo "  ✅ 详细的TTS合成报告"
echo ""
echo "📝 支持的TTS模型:"
echo "  🔊 speech-01: 标准质量"
echo "  🔊 speech-01-hd: 高清质量"
echo "  🔊 speech-02: 标准质量v2"
echo "  🔊 speech-02-hd: 高清质量v2 (推荐)"
echo ""
echo "🎵 支持的声音类型:"
echo "  👨 男声: 青涩青年、精英、霸道、大学生"
echo "  👩 女声: 青涩青年、精英、霸道、大学生、少女、御姐、成熟、甜美"
echo ""
echo "🚀 使用流程:"
echo "  1️⃣  输入Minimax API Key"
echo "  2️⃣  选择TTS模型和声音"
echo "  3️⃣  输入要合成的文本"
echo "  4️⃣  上传视频文件"
echo "  5️⃣  配置动作控制参数"
echo "  6️⃣  点击生成按钮"
echo ""
echo "🔧 监控命令:"
echo "  查看日志: sudo docker exec heygem-service tail -f /workspace/tts_digital_human.log"
echo "  停止服务: sudo docker exec heygem-service pkill -f app_tts_digital_human.py"
echo ""
echo "⚠️  注意: 需要有效的Minimax API Key，调用会消耗tokens"
echo ""
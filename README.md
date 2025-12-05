# Avatar MiniMax TTS

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://github.com/backearth1/heygem-h200)
![Python](https://img.shields.io/badge/Python-3.8-blue.svg)
![GPU](https://img.shields.io/badge/GPU-H200%20Supported-brightgreen.svg)

## 项目简介

基于MiniMax高拟人tts驱动的数字人项目，支持头部动作控制，提供完整的Docker容器化，本项目采用MiniMax M2的vibe coding，在Heygem项目基础上优化而来。

<img width="917" height="849" alt="image" src="https://github.com/user-attachments/assets/abb99e90-4f50-4c55-be41-f94feac0288d" />


## 🚀 主要特性

### 🎭 动作控制系统
- **智能动作识别**: 基于音频特征和语义内容自动生成头部动作
- **多种动作模式**: 点头、摇头、思考歪头等头部动作
- **动作强度控制**: 0.1-2.0倍可调节动作幅度
- **实时动作分析**: 详细的动作参数和执行报告

### 后续待扩展功能
- 手部动作驱动
- 面部情感驱动
- 基于文本和声音的LLM自动驱动标签


## 📋 环境要求

- **操作系统**: Linux (Ubuntu 18.04+)
- **GPU**:  目前仅适配H200,建议自己根据硬件修改对应驱动
- **软件**: Docker 20.10+, NVIDIA Docker Runtime
- **内存**: 建议16GB+ RAM, 8GB+ GPU内存

## 🛠️ 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/backearth1/heygem-h200.git
cd heygem-h200
```

### 2. 下载模型文件
```bash
bash download.sh
```

### 3. 构建Docker镜像
```bash
# 基础版本
bash run_docker.sh

# H200优化版本
docker build -f Dockerfile.h200 -t heygem-h200:latest .
```

### 4. 启动服务

#### 基础服务
```bash
bash start_h200_daemon.sh
```

#### 动作增强版本
```bash
bash start_motion_enhanced.sh
```

#### 情感驱动版本
```bash
bash start_emotion_system.sh
```

## 🌟 服务访问

启动后可通过以下地址访问：

-  http://localhost:7860


## 📚 使用指南

### 基础使用
1. 访问Web界面
2. 上传音频文件（.wav/.mp3）
3. 上传视频文件（.mp4/.avi）
4. 点击"生成"按钮
5. 等待处理完成并下载结果

### 动作控制使用
1. 展开"🎭 动作控制选项"
2. 选择动作类型（点头/摇头/思考/强调）
3. 调整动作强度（0.1-2.0）
4. 提交生成任务
5. 查看"📊 动作分析报告"


## 🔧 管理命令

### 服务管理
```bash
# 查看服务状态
sudo docker ps | grep heygem

# 查看日志
sudo docker exec heygem-service tail -f /workspace/app.log

# 停止服务
bash stop_h200_service.sh

# 重启服务
bash start_h200_daemon.sh
```

### 系统维护
```bash
# 检查GPU状态
nvidia-smi

# 检查PyTorch兼容性
bash fix_pytorch_and_test.sh

# 测试服务
bash test_h200_service.sh
```

## 📖 详细文档

更多详细信息请参考：
- [项目文档](CLAUDE.md) - 完整的技术文档和配置说明
- [服务管理](SERVICE_MANAGEMENT.md) - 服务管理和故障排除指南

## 🤝 贡献

欢迎提交Issues和Pull Requests！

## 📄 许可证

本项目基于原HeyGem.ai协议。

## ⭐ Star History

如果这个项目对您有帮助，请给我们一个Star！

---

**🤖 Powered by MiniMax M2** - 高拟真tts驱动的数字人

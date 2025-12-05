
# Avatar MiniMax TTS

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://github.com/backearth1/heygem-h200)
![Python](https://img.shields.io/badge/Python-3.8-blue.svg)
![GPU](https://img.shields.io/badge/GPU-H200%20Supported-brightgreen.svg)

**[中文](./README.md)** | **[English](#english-version)**

---

<a name="english-version"></a>

## Project Overview

A digital human project driven by MiniMax high-fidelity TTS, supporting head motion control and complete Docker containerization. This project uses MiniMax M2's vibe coding and is optimized based on the Heygem project.

<img width="917" height="849" alt="image" src="https://github.com/user-attachments/assets/abb99e90-4f50-4c55-be41-f94feac0288d" />

## 🚀 Key Features

### 🎭 Motion Control System
- **Intelligent Motion Recognition**: Automatically generate head movements based on audio features and semantic content
- **Multiple Motion Modes**: Nodding, head shaking, thinking tilt and other head movements
- **Motion Intensity Control**: Adjustable motion amplitude from 0.1-2.0x
- **Real-time Motion Analysis**: Detailed motion parameters and execution reports

### Upcoming Extensions
- Hand motion control
- Facial emotion-driven expressions
- LLM-based automatic tagging driven by text and sound

## 📋 Requirements

- **Operating System**: Linux (Ubuntu 18.04+)
- **GPU**: Currently optimized for H200, recommend adapting drivers based on your hardware
- **Software**: Docker 20.10+, NVIDIA Docker Runtime
- **Memory**: Recommended 16GB+ RAM, 8GB+ GPU memory

## 🛠️ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/backearth1/heygem-h200.git
cd heygem-h200
```

### 2. Download Model Files
```bash
bash download.sh
```

### 3. Build Docker Image
```bash
# Basic version
bash run_docker.sh

# H200 optimized version
docker build -f Dockerfile.h200 -t heygem-h200:latest .
```

### 4. Start Services

#### Basic Service
```bash
bash start_h200_daemon.sh
```

#### Motion Enhanced Version
```bash
bash start_motion_enhanced.sh
```

#### Emotion-Driven Version
```bash
bash start_emotion_system.sh
```

## 🌟 Service Access

After startup, access via:

-  http://localhost:7860

## 📚 Usage Guide

### Basic Usage
1. Access the Web interface
2. Upload audio file (.wav/.mp3)
3. Upload video file (.mp4/.avi)
4. Click "Generate" button
5. Wait for processing completion and download results

### Motion Control Usage
1. Expand "🎭 Motion Control Options"
2. Select motion type (nod/shake/think/emphasize)
3. Adjust motion intensity (0.1-2.0)
4. Submit generation task
5. View "📊 Motion Analysis Report"

## 🔧 Management Commands

### Service Management
```bash
# Check service status
sudo docker ps | grep heygem

# View logs
sudo docker exec heygem-service tail -f /workspace/app.log

# Stop service
bash stop_h200_service.sh

# Restart service
bash start_h200_daemon.sh
```

### System Maintenance
```bash
# Check GPU status
nvidia-smi

# Check PyTorch compatibility
bash fix_pytorch_and_test.sh

# Test service
bash test_h200_service.sh
```

## 📖 Documentation

For more detailed information, refer to:
- [Project Documentation](CLAUDE.md) - Complete technical documentation and configuration guide
- [Service Management](SERVICE_MANAGEMENT.md) - Service management and troubleshooting guide

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

This project is based on the original HeyGem.ai license.

## ⭐ Star History

If this project helps you, please give us a Star!

---

**🤖 Powered by MiniMax M2** - High-fidelity TTS-driven digital human

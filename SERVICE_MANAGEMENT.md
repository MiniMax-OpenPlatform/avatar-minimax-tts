# HeyGem数字人服务管理指南

## 📋 当前状态

**✅ 服务正在运行**
- 容器ID: `b71eb09b41bb`
- 访问地址: http://localhost:7860
- GPU支持: NVIDIA H200 (PyTorch 2.0.0+cu118)

## 🔄 退出Claude Code后的行为

### 当前服务
当前运行的服务**会继续运行**，但存在以下风险：
- ✅ 退出Claude Code不会停止服务
- ⚠️ 如果后台bash进程被终止，容器会停止
- ⚠️ 使用了`--rm`参数，容器停止后会自动删除

### 推荐方案
使用守护进程模式启动，确保长期稳定运行。

## 📝 服务管理命令

### 1. 查看当前运行状态
```bash
sudo docker ps | grep heygem
```

### 2. 查看服务日志
```bash
# 查看当前容器的实时日志
sudo docker logs -f b71eb09b41bb

# 如果使用守护进程模式启动
sudo docker logs -f heygem-service
```

### 3. 停止当前服务
```bash
# 方式1: 使用停止脚本（推荐）
bash stop_h200_service.sh

# 方式2: 手动停止
sudo docker stop b71eb09b41bb
```

### 4. 启动守护进程服务（推荐）
```bash
# 先停止当前服务
bash stop_h200_service.sh

# 启动守护进程模式
bash start_h200_daemon.sh
```

## 🚀 守护进程模式 vs 当前模式

| 特性 | 当前模式 | 守护进程模式 |
|------|---------|-------------|
| 退出Claude Code后 | ⚠️ 可能停止 | ✅ 继续运行 |
| 自动重启 | ❌ 否 | ✅ 是（unless-stopped） |
| 容器删除 | ✅ 自动删除（--rm） | ❌ 保留容器 |
| 日志持久化 | ⚠️ 有限 | ✅ 完整保留 |
| 稳定性 | ⚠️ 中等 | ✅ 高 |

## 🛠️ 常用维护命令

### 检查GPU使用情况
```bash
nvidia-smi
```

### 检查容器资源占用
```bash
sudo docker stats b71eb09b41bb
```

### 重启服务
```bash
# 守护进程模式
sudo docker restart heygem-service

# 当前模式（需要重新运行启动脚本）
sudo docker stop b71eb09b41bb
bash start_h200_service.sh
```

### 查看生成的视频
```bash
ls -lh result/*/
```

### 清理旧的结果文件
```bash
# 查看所有结果
du -sh result/*

# 删除特定任务的结果
rm -rf result/<work_id>/
```

## ⚙️ 配置说明

### 端口
- **7860**: Gradio Web界面

### 数据目录
- `result/`: 生成的视频文件
- `/tmp/gradio/`: 上传的临时文件（在容器内）

### GPU配置
- PyTorch版本: 2.0.0+cu118
- CUDA版本: 11.8.0
- 支持架构: sm_90 (H200)

## 🐛 已知问题

### stream.ts错误
- **现象**: 浏览器控制台显示"Method not implemented"
- **影响**: 仅影响文件上传进度显示
- **解决**: 已通过`queue=False`最小化影响
- **状态**: 不影响实际功能，可忽略

## 📞 故障排查

### 服务无法访问
```bash
# 1. 检查容器是否运行
sudo docker ps | grep heygem

# 2. 检查端口占用
sudo netstat -tulpn | grep 7860

# 3. 查看容器日志
sudo docker logs b71eb09b41bb | tail -50
```

### GPU不可用
```bash
# 1. 检查NVIDIA驱动
nvidia-smi

# 2. 检查Docker GPU支持
sudo docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu20.04 nvidia-smi
```

### 视频生成失败
```bash
# 查看详细日志
sudo docker logs b71eb09b41bb 2>&1 | grep -E "(ERROR|error|失败)"
```

## 📊 性能参考

- **处理速度**: ~40帧/秒
- **GPU利用率**: 100%（处理时）
- **内存使用**: ~7-8GB显存
- **示例**: 112秒音频 + 16秒视频 → 60秒生成时间

## 🔐 安全建议

1. 不要暴露7860端口到公网（当前仅localhost）
2. 定期清理result目录中的旧文件
3. 监控GPU温度和使用率
4. 使用`--restart unless-stopped`确保服务稳定性

## 📝 更新日志

- **2025-12-03**: 修复H200 GPU兼容性（PyTorch 2.0.0+cu118）
- **2025-12-03**: 修复Gradio stream.ts错误（queue=False）
- **2025-12-03**: 创建守护进程启动脚本

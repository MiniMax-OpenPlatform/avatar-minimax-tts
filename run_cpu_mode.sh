#!/bin/bash

# CPU模式运行数字人服务
# 优点：100%兼容，稳定运行
# 缺点：速度慢（可能慢50-100倍）

echo "======================================"
echo "CPU模式 - 数字人服务"
echo "警告：CPU模式速度较慢，但保证能运行"
echo "======================================"

sudo docker run --rm \
  -v "$(pwd)":/workspace \
  -w /workspace \
  -p 7860:7860 \
  -e CUDA_VISIBLE_DEVICES="" \
  heygem-digital-human:latest \
  /usr/local/python38/bin/python3.8 app.py

echo "======================================"
echo "服务已停止"
echo "======================================"

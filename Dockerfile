# 使用本地已有的CUDA镜像
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# 设置代理（构建时使用）
ARG HTTP_PROXY=http://pac-internal.xaminim.com:3129
ARG HTTPS_PROXY=http://pac-internal.xaminim.com:3129
ENV http_proxy=${HTTP_PROXY}
ENV https_proxy=${HTTPS_PROXY}

# 设置时区和基础环境
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

# 更换为阿里云Ubuntu镜像源
RUN sed -i 's@//.*archive.ubuntu.com@//mirrors.aliyun.com@g' /etc/apt/sources.list && \
    sed -i 's@//.*security.ubuntu.com@//mirrors.aliyun.com@g' /etc/apt/sources.list

# 安装基础工具和Python编译所需的依赖
RUN apt-get update && apt-get install -y \
    software-properties-common \
    wget \
    curl \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    libbz2-dev \
    liblzma-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制本地Python源码并编译安装（去掉优化选项加快编译，跳过ensurepip）
COPY Python-3.8.18.tgz /tmp/
RUN cd /tmp && \
    tar -xzf Python-3.8.18.tgz && \
    cd Python-3.8.18 && \
    ./configure --prefix=/usr/local/python38 --without-ensurepip && \
    make -j$(nproc) && \
    make install && \
    cd / && rm -rf /tmp/Python-3.8.18*

# 手动安装pip (使用Python 3.8专用版本)
RUN cd /tmp && \
    wget https://bootstrap.pypa.io/pip/3.8/get-pip.py && \
    /usr/local/python38/bin/python3.8 get-pip.py && \
    rm -f get-pip.py

# 创建Python 3.8的符号链接
RUN ln -sf /usr/local/python38/bin/python3.8 /usr/bin/python && \
    ln -sf /usr/local/python38/bin/python3.8 /usr/bin/python3 && \
    ln -sf /usr/local/python38/bin/pip3.8 /usr/bin/pip

# 安装其他系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    vim \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 升级pip并配置国内镜像源
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 设置工作目录
WORKDIR /workspace

# 复制requirements.txt
COPY requirements.txt .

# 安装PyTorch (CUDA 11.3版本)
RUN pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0+cu113 \
    -f https://download.pytorch.org/whl/cu113/torch_stable.html

# 安装onnxruntime-gpu
RUN pip install onnxruntime-gpu==1.16.0

# 安装其他依赖
RUN pip install -r requirements.txt

# 单独安装gradio和flask（允许依赖冲突）
RUN pip install gradio==4.44.1 flask==3.0.3 --no-deps && \
    pip install importlib-resources \
    "aiofiles<24.0,>=22.0" \
    anyio \
    fastapi \
    ffmpy \
    gradio-client==1.3.0 \
    httpx \
    "huggingface-hub>=0.19.3" \
    jinja2 \
    markupsafe \
    orjson \
    pandas \
    pydantic \
    pydantic-core \
    pydub \
    python-multipart \
    ruff \
    semantic-version \
    tomlkit==0.12.0 \
    typer \
    "urllib3~=2.0" \
    uvicorn \
    websockets \
    starlette \
    werkzeug \
    blinker \
    itsdangerous

# 取消代理设置（运行时不需要）
ENV http_proxy=
ENV https_proxy=

# 暴露Gradio端口
EXPOSE 7860

# 默认启动bash
CMD ["/bin/bash"]

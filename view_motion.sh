#!/bin/bash

# 设置错误时退出
set -e

# 激活 conda 环境
echo "正在激活 isaacgym 环境..."
source /home/yyang52/miniconda/bin/activate isaacgym

# 设置工作目录
cd "$(dirname "$0")"

# 设置 Python 路径
export PYTHONPATH=$PYTHONPATH:.

# 查看动作
echo "正在运行查看器..."
python ase/poselib/view_motion.py 
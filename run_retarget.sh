#!/bin/bash

# 设置错误时退出
set -e

# 解析命令行参数
VISUALIZE=true
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-visualize)
            VISUALIZE=false
            shift
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 激活 conda 环境
echo "正在激活 isaacgym 环境..."
source /home/yyang52/miniconda/bin/activate isaacgym

# 设置工作目录
cd "$(dirname "$0")"

# 首先转换 fbx 到 npy
echo "正在转换 FBX 文件到 NPY 格式..."
if [ "$VISUALIZE" = true ]; then
    python ase/poselib/fbx_importer.py
else
    python ase/poselib/fbx_importer.py --no-visualize
fi

# 运行重定向程序
echo "正在运行动作重定向..."
if [ "$VISUALIZE" = true ]; then
    python ase/poselib/retarget_motion.py
else
    python ase/poselib/retarget_motion.py --no-visualize
fi

echo "完成！" 
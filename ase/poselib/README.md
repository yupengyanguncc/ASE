# poselib

`poselib` is a library for loading, manipulating, and retargeting skeleton poses and motions. It is separated into three modules: `poselib.core` for basic data loading and tensor operations, `poselib.skeleton` for higher-level skeleton operations, and `poselib.visualization` for displaying skeleton poses. This library is built on top of the PyTorch framework and requires data to be in PyTorch tensors.

## poselib.core
- `poselib.core.rotation3d`: A set of Torch JIT functions for computing quaternions, transforms, and rotation/transformation matrices.
    - `quat_*` manipulate and create quaternions in [x, y, z, w] format (where w is the real component).
    - `transform_*` handle 7D transforms in [quat, pos] format.
    - `rot_matrix_*` handle 3x3 rotation matrices.
    - `euclidean_*` handle 4x4 Euclidean transformation matrices.
- `poselib.core.tensor_utils`: Provides loading and saving functions for PyTorch tensors.

## poselib.skeleton
- `poselib.skeleton.skeleton3d`: Utilities for loading and manipulating skeleton poses, and retargeting poses to different skeletons.
    - `SkeletonTree` is a class that stores a skeleton as a tree structure. This describes the skeleton topology and joints.
    - `SkeletonState` describes the static state of a skeleton, and provides both global and local joint angles.
    - `SkeletonMotion` describes a time-series of skeleton states and provides utilities for computing joint velocities.

## poselib.visualization
- `poselib.visualization.common`: Functions used for visualizing skeletons interactively in `matplotlib`.
    - In SkeletonState visualization, use key `q` to quit window.
    - In interactive SkeletonMotion visualization, you can use the following key commands:
        - `w` - loop animation
        - `x` - play/pause animation
        - `z` - previous frame
        - `c` - next frame
        - `n` - quit window

## Key Features
Poselib provides several key features for working with animation data. We list some of the frequently used ones here, and provide instructions and examples on their usage.

### Importing from FBX
Poselib supports importing skeletal animation sequences from .fbx format into a SkeletonMotion representation. To use this functionality, you will need to first set up the Python FBX SDK on your machine using the following instructions.

This package is necessary to read data from fbx files, which is a proprietary file format owned by Autodesk. The latest FBX SDK tested was FBX SDK 2020.2.1 for Python 3.7, which can be found on the Autodesk website: https://www.autodesk.com/developer-network/platform-technologies/fbx-sdk-2020-2-1.

Follow the instructions at https://help.autodesk.com/view/FBX/2020/ENU/?guid=FBX_Developer_Help_scripting_with_python_fbx_installing_python_fbx_html for download, install, and copy/paste instructions for the FBX Python SDK.

This repo provides an example script `fbx_importer.py` that shows usage of importing a .fbx file. Note that `SkeletonMotion.from_fbx()` takes in an optional parameter `root_joint`, which can be used to specify a joint in the skeleton tree as the root joint. If `root_joint` is not specified, we will default to using the first node in the FBX scene that contains animation data. 

### Importing from MJCF
MJCF is a robotics file format supported by Isaac Gym. For convenience, we provide an API for importing MJCF assets into SkeletonTree definitions to represent the skeleton topology. An example script `mjcf_importer.py` is provided to show usage of this.

This can be helpful if motion sequences need to be retargeted to your simulation skeleton that's been created in MJCF format. Importing the file to SkeletonTree format will allow you to generate T-poses or other retargeting poses that can be used for retargeting. We also show an example of creating a T-Pose for our AMP Humanoid asset in `generate_amp_humanoid_tpose.py`.

### Retargeting Motions
Retargeting motions is important when your source data uses skeletons that have different morphologies than your target skeletons. We provide APIs for performing retarget of motion sequences in our SkeletonState and SkeletonMotion classes.

To use the retargeting API, users must provide the following information:
  - source_motion: a SkeletonMotion npy representation of a motion sequence. The motion clip should use the same skeleton as the source T-Pose skeleton.
  - target_motion_path: path to save the retargeted motion to
  - source_tpose: a SkeletonState npy representation of the source skeleton in it's T-Pose state
  - target_tpose: a SkeletonState npy representation of the target skeleton in it's T-Pose state (pose should match source T-Pose)
  - joint_mapping: mapping of joint names from source to target
  - rotation: root rotation offset from source to target skeleton (for transforming across different orientation axes), represented as a quaternion in XYZW order.
  - scale: scale offset from source to target skeleton

We provide an example script `retarget_motion.py` to demonstrate usage of the retargeting API for the CMU Motion Capture Database. Note that the retargeting data for this script is stored in `data/configs/retarget_cmu_to_amp.json`.

Additionally, a SkeletonState T-Pose file and retargeting config file are also provided for the SFU Motion Capture Database. These can be found at `data/sfu_tpose.npy` and `data/configs/retarget_sfu_to_amp.json`.

### Documentation
We provide a description of the functions and classes available in poselib in the comments of the APIs. Please check them out for more details.

# 动作重定向系统 (Motion Retargeting System)

## 系统概述

这是一个基于骨骼的动作重定向系统，用于将动作从一个骨骼结构映射到另一个骨骼结构。系统支持：
- FBX动作文件的导入和转换
- 骨骼动作的重定向
- 动作的可视化比较
- 实时动作预览

## 核心组件

### 1. 骨骼树 (SkeletonTree)
```python
class SkeletonTree:
    """
    表示骨骼结构的树形结构
    - node_names: 关节名称列表
    - parent_indices: 父关节索引
    - local_translation: 局部平移
    """
```

### 2. 骨骼状态 (SkeletonState)
```python
class SkeletonState:
    """
    表示骨骼在某一时刻的状态
    - local_rotation: 局部旋转
    - global_rotation: 全局旋转
    - root_translation: 根节点位置
    """
```

### 3. 骨骼动作 (SkeletonMotion)
```python
class SkeletonMotion:
    """
    表示完整的动作序列
    - fps: 帧率
    - global_velocity: 全局速度
    - global_angular_velocity: 全局角速度
    """
```

## 主要功能

### 1. 动作重定向 (retarget_to)
```python
def retarget_to(self, joint_mapping, source_tpose, target_tpose, ...):
    """
    将动作从源骨骼重定向到目标骨骼
    步骤：
    1. 预处理：创建源和目标T-pose
    2. 过滤无关关节
    3. 对齐旋转
    4. 调整缩放
    5. 应用全局旋转
    6. 组合最终结果
    """
```

### 2. 骨骼映射 (_remapped_to)
```python
def _remapped_to(self, joint_mapping, target_skeleton_tree):
    """
    根据关节映射关系重新映射骨骼状态
    - 创建反向映射
    - 保留目标骨骼中的相关关节
    - 映射局部旋转
    """
```

### 3. 骨骼转换 (_transfer_to)
```python
def _transfer_to(self, new_skeleton_tree):
    """
    将骨骼状态转移到新的骨骼树
    - 保持全局旋转
    - 保持根节点位置
    - 适应新的骨骼结构
    """
```

## 使用示例

### 1. 导入动作
```python
# 从FBX文件导入动作
motion = SkeletonMotion.from_fbx(
    fbx_file_path="path/to/motion.fbx",
    fps=120
)
```

### 2. 重定向动作
```python
# 定义关节映射关系
joint_mapping = {
    "source_hip": "target_hip",
    "source_knee": "target_knee",
    # ... 更多映射
}

# 执行重定向
retargeted_motion = source_motion.retarget_to(
    joint_mapping=joint_mapping,
    source_tpose=source_tpose,
    target_tpose=target_tpose,
    rotation_to_target_skeleton=rotation,
    scale_to_target_skeleton=scale
)
```

### 3. 可视化比较
```python
# 使用compare_motions.py比较原始动作和重定向后的动作
python compare_motions.py
```

## 关键概念

### 1. T-pose
- 骨骼的参考姿态
- 用于计算相对旋转
- 确保动作映射的准确性

### 2. 关节映射
- 源骨骼到目标骨骼的对应关系
- 确保动作语义的保持
- 处理不同骨骼结构的差异

### 3. 旋转表示
- 使用四元数表示旋转
- 支持局部和全局旋转
- 确保动作的连续性

## 注意事项

1. 骨骼结构
   - 确保源骨骼和目标骨骼有足够的对应关节
   - 处理缺失关节的情况
   - 保持骨骼层次结构的合理性

2. 动作质量
   - 检查重定向后的动作连续性
   - 确保动作的自然性
   - 验证关节限制

3. 性能考虑
   - 优化计算效率
   - 处理大规模动作数据
   - 内存使用优化

## 依赖项

- Python 3.6+
- PyTorch
- NumPy
- Matplotlib
- FBX SDK

## 文件结构

```
poselib/
├── skeleton/
│   ├── skeleton3d.py    # 骨骼核心类
│   └── ...
├── core/
│   ├── rotation3d.py    # 旋转计算
│   └── ...
├── visualization/
│   ├── common.py        # 可视化工具
│   └── ...
└── data/
    ├── configs/         # 配置文件
    └── ...
```

## 未来改进

1. 功能扩展
   - 支持更多动作格式
   - 添加动作编辑功能
   - 增强可视化能力

2. 性能优化
   - 并行计算支持
   - 内存使用优化
   - 实时处理能力

3. 用户体验
   - 交互式界面
   - 批量处理支持
   - 更多调试工具

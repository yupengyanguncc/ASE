import os
import sys
from isaacgym.torch_utils import *
import torch
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from poselib.core.rotation3d import *
from poselib.skeleton.skeleton3d import SkeletonTree, SkeletonState, SkeletonMotion
from poselib.visualization.common import plot_skeleton_state, plot_skeleton_motion_interactive

def plot_skeleton_frame(motion, frame_idx=0, ax=None):
    if ax is None:
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
    
    # 获取骨骼位置
    positions = motion.global_translation[frame_idx].numpy()
    
    # 绘制关节点
    ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2], c='r', marker='o')
    
    # 绘制骨骼连接
    for joint_name, joint_idx in motion.skeleton_tree._node_indices.items():
        if joint_name != "pelvis":  # 跳过根节点
            parent_idx = motion.skeleton_tree._parent_indices[joint_idx]
            start = positions[parent_idx]
            end = positions[joint_idx]
            ax.plot([start[0], end[0]], [start[1], end[1]], [start[2], end[2]], 'b-')
    
    # 设置视角和标签
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'Frame {frame_idx}')
    
    # 设置坐标轴范围
    min_val = positions.min()
    max_val = positions.max()
    margin = (max_val - min_val) * 0.1
    ax.set_xlim([min_val - margin, max_val + margin])
    ax.set_ylim([min_val - margin, max_val + margin])
    ax.set_zlim([min_val - margin, max_val + margin])
    
    return ax

def main():
    try:
        print("正在加载动作文件...")
        motion_file = "ase/poselib/data/01_01_cmu_amp.npy"
        
        if not os.path.exists(motion_file):
            print(f"错误：找不到动作文件 {motion_file}")
            return
            
        motion = SkeletonMotion.from_file(motion_file)
        print(f"动作加载成功！")
        print(f"- 帧数: {motion.local_rotation.shape[0]}")
        print(f"- FPS: {motion.fps}")
        print(f"- 关节数: {len(motion.skeleton_tree._node_indices)}")
        print("\n使用方向键或鼠标滚轮浏览不同帧，关闭窗口退出。")
        
        # 创建图形窗口
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
        frame_idx = [0]  # 使用列表以便在回调函数中修改
        
        def on_key(event):
            if event.key == 'right':
                frame_idx[0] = (frame_idx[0] + 1) % motion.local_rotation.shape[0]
            elif event.key == 'left':
                frame_idx[0] = (frame_idx[0] - 1) % motion.local_rotation.shape[0]
            ax.clear()
            plot_skeleton_frame(motion, frame_idx[0], ax)
            plt.draw()
        
        def on_scroll(event):
            if event.button == 'up':
                frame_idx[0] = (frame_idx[0] + 1) % motion.local_rotation.shape[0]
            elif event.button == 'down':
                frame_idx[0] = (frame_idx[0] - 1) % motion.local_rotation.shape[0]
            ax.clear()
            plot_skeleton_frame(motion, frame_idx[0], ax)
            plt.draw()
        
        # 绑定事件处理函数
        fig.canvas.mpl_connect('key_press_event', on_key)
        fig.canvas.mpl_connect('scroll_event', on_scroll)
        
        # 显示第一帧
        plot_skeleton_frame(motion, frame_idx[0], ax)
        plt.show()
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
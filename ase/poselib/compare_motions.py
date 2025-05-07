import os
import sys
from isaacgym.torch_utils import *
import torch
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider

from poselib.core.rotation3d import *
from poselib.skeleton.skeleton3d import SkeletonTree, SkeletonState, SkeletonMotion
from poselib.visualization.common import plot_skeleton_state, plot_skeleton_motion_interactive

def get_motion_bounds(motion):
    """Calculate the bounds of the motion"""
    positions = motion.global_translation.numpy()
    x_min, x_max = positions[:, 0].min(), positions[:, 0].max()
    y_min, y_max = positions[:, 1].min(), positions[:, 1].max()
    z_min, z_max = positions[:, 2].min(), positions[:, 2].max()
    
    # Add some padding
    padding = 0.1
    x_range = x_max - x_min
    y_range = y_max - y_min
    z_range = z_max - z_min
    
    return {
        'x': (x_min - padding * x_range, x_max + padding * x_range),
        'y': (y_min - padding * y_range, y_max + padding * y_range),
        'z': (z_min - padding * z_range, z_max + padding * z_range)
    }

def plot_skeleton_frame(motion, frame_idx=0, ax=None, color='r', label=None):
    if ax is None:
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
    
    # Get bone positions
    positions = motion.global_translation[frame_idx].numpy()
    
    # Plot joints
    ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2], c=color, marker='o', label=label, s=50)
    
    # Plot bone connections
    for joint_name, joint_idx in motion.skeleton_tree._node_indices.items():
        if joint_name != "pelvis":  # Skip root node
            parent_idx = motion.skeleton_tree._parent_indices[joint_idx]
            start = positions[parent_idx]
            end = positions[joint_idx]
            ax.plot([start[0], end[0]], [start[1], end[1]], [start[2], end[2]], color=color, linestyle='-', linewidth=2)
    
    return ax

def main():
    try:
        print("Loading motion files...")
        source_file = "ase/poselib/data/01_01_cmu.npy"
        target_file = "ase/poselib/data/01_01_cmu_amp.npy"
        
        if not os.path.exists(source_file):
            print(f"Error: Source motion file not found: {source_file}")
            return
            
        if not os.path.exists(target_file):
            print(f"Error: Target motion file not found: {target_file}")
            return
            
        source_motion = SkeletonMotion.from_file(source_file)
        target_motion = SkeletonMotion.from_file(target_file)
        
        # Calculate bounds for both motions
        source_bounds = get_motion_bounds(source_motion)
        target_bounds = get_motion_bounds(target_motion)
        
        print(f"Motions loaded successfully!")
        print(f"Source motion:")
        print(f"- Frames: {source_motion.local_rotation.shape[0]}")
        print(f"- FPS: {source_motion.fps}")
        print(f"- Joints: {len(source_motion.skeleton_tree._node_indices)}")
        print(f"- Bounds: X{source_bounds['x']}, Y{source_bounds['y']}, Z{source_bounds['z']}")
        print(f"\nTarget motion:")
        print(f"- Frames: {target_motion.local_rotation.shape[0]}")
        print(f"- FPS: {target_motion.fps}")
        print(f"- Joints: {len(target_motion.skeleton_tree._node_indices)}")
        print(f"- Bounds: X{target_bounds['x']}, Y{target_bounds['y']}, Z{target_bounds['z']}")
        print("\nControls:")
        print("- Play/Pause: Space")
        print("- Next/Previous frame: Right/Left arrow keys")
        print("- Speed control: Slider")
        print("- Close window to exit")
        
        # Create figure window
        fig = plt.figure(figsize=(15, 10))
        
        # Create two subplots
        ax1 = fig.add_subplot(121, projection='3d')
        ax2 = fig.add_subplot(122, projection='3d')
        
        # Add control panel
        plt.subplots_adjust(bottom=0.2)
        
        # Create play/pause button
        play_ax = plt.axes([0.4, 0.05, 0.2, 0.075])
        play_button = Button(play_ax, 'Play/Pause')
        
        # Create speed slider
        speed_ax = plt.axes([0.2, 0.15, 0.6, 0.03])
        speed_slider = Slider(speed_ax, 'Speed', 0.1, 2.0, valinit=1.0)
        
        frame_idx = [0]  # Use list for callback function
        is_playing = [False]  # Use list for play state
        animation = [None]  # Use list for animation object
        
        def update_plot():
            ax1.clear()
            ax2.clear()
            
            # Plot source motion
            plot_skeleton_frame(source_motion, frame_idx[0], ax1, color='r', label='Source')
            ax1.set_title(f'Source Motion - Frame {frame_idx[0]}')
            ax1.set_xlabel('X')
            ax1.set_ylabel('Y')
            ax1.set_zlabel('Z')
            
            # Plot target motion
            plot_skeleton_frame(target_motion, frame_idx[0], ax2, color='b', label='Target')
            ax2.set_title(f'Target Motion - Frame {frame_idx[0]}')
            ax2.set_xlabel('X')
            ax2.set_ylabel('Y')
            ax2.set_zlabel('Z')
            
            # Set axis limits for each motion
            ax1.set_xlim(source_bounds['x'])
            ax1.set_ylim(source_bounds['y'])
            ax1.set_zlim(source_bounds['z'])
            
            ax2.set_xlim(target_bounds['x'])
            ax2.set_ylim(target_bounds['y'])
            ax2.set_zlim(target_bounds['z'])
            
            # Set default view angle
            for ax in [ax1, ax2]:
                ax.view_init(elev=20, azim=45)
            
            plt.draw()
        
        def play_pause(event):
            is_playing[0] = not is_playing[0]
            if is_playing[0]:
                if animation[0] is None:
                    def update(frame):
                        frame_idx[0] = frame
                        update_plot()
                        return []
                    
                    animation[0] = animation.FuncAnimation(
                        fig, update,
                        frames=range(min(source_motion.local_rotation.shape[0], target_motion.local_rotation.shape[0])),
                        interval=1000/source_motion.fps/speed_slider.val,
                        repeat=True
                    )
            else:
                if animation[0] is not None:
                    animation[0].event_source.stop()
                    animation[0] = None
        
        def on_key(event):
            if event.key == 'right':
                frame_idx[0] = (frame_idx[0] + 1) % min(source_motion.local_rotation.shape[0], target_motion.local_rotation.shape[0])
            elif event.key == 'left':
                frame_idx[0] = (frame_idx[0] - 1) % min(source_motion.local_rotation.shape[0], target_motion.local_rotation.shape[0])
            elif event.key == ' ':  # Space key
                play_pause(None)
            update_plot()
        
        def on_scroll(event):
            if event.button == 'up':
                frame_idx[0] = (frame_idx[0] + 1) % min(source_motion.local_rotation.shape[0], target_motion.local_rotation.shape[0])
            elif event.button == 'down':
                frame_idx[0] = (frame_idx[0] - 1) % min(source_motion.local_rotation.shape[0], target_motion.local_rotation.shape[0])
            update_plot()
        
        def on_speed_change(val):
            if animation[0] is not None:
                animation[0].event_source.interval = 1000/source_motion.fps/val
        
        # Bind event handlers
        fig.canvas.mpl_connect('key_press_event', on_key)
        fig.canvas.mpl_connect('scroll_event', on_scroll)
        play_button.on_clicked(play_pause)
        speed_slider.on_changed(on_speed_change)
        
        # Show first frame
        update_plot()
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main() 
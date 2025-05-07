#!/bin/bash

# 激活 conda 环境
source /home/yyang52/miniconda/bin/activate isaacgym

# 运行演示程序
python ase/run.py \
    --test \
    --task HumanoidHeading \
    --num_envs 16 \
    --cfg_env ase/data/cfg/humanoid_sword_shield_heading.yaml \
    --cfg_train ase/data/cfg/train/rlg/hrl_humanoid.yaml \
    --motion_file ase/data/motions/reallusion_sword_shield/RL_Avatar_Idle_Ready_Motion.npy \
    --llc_checkpoint ase/data/models/ase_llc_reallusion_sword_shield.pth \
    --checkpoint ase/data/models/ase_hlc_heading_reallusion_sword_shield.pth 
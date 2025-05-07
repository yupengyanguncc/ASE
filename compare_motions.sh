#!/bin/bash

# Exit on error
set -e

# Activate conda environment
echo "Activating isaacgym environment..."
source /home/yyang52/miniconda/bin/activate isaacgym

# Set working directory
cd "$(dirname "$0")"

# Set Python path
export PYTHONPATH=$PYTHONPATH:.

# Run comparison program
echo "Running motion comparison program..."
python ase/poselib/compare_motions.py 
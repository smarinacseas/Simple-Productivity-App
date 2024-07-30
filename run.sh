#!/bin/bash

# Ensure the script exits on any error
set -e

# Source the Conda profile script to enable the `conda` command
source /opt/anaconda3/etc/profile.d/conda.sh

# Activate the Conda environment named 'quant'
conda activate quant

# Run the Python script
python /Users/stefanmarinac/VSCode_Projects/Simple-Productivity-App/productivity.py
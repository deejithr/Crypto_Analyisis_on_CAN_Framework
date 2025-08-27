#!/bin/bash

# Install the required python Libraries
pip install -r requirements.txt

# Setting up the VCAN
sudo -S modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
#!/bin/bash

# Setting up the VCAN
echo "Setting up Vcan0..."
sudo -S modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
echo "done..."
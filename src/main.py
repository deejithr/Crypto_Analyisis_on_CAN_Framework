"""
This module is the main entry point.

It includes :
    * Start/Stop the simulation

"""
################################################################################
# Imports
################################################################################
import os, sys
from CAN_Simulation.simulate import *

################################################################################
# Main
################################################################################
if __name__ == "__main__":
    start_simulation()

    # Run the simulation for 10 seconds
    time.sleep(10)

    stop_simulation()
    

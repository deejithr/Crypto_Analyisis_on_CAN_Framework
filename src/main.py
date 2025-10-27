"""
This module is the main entry point.

It includes :
    * Start/Stop the simulation

"""
################################################################################
# Imports
################################################################################
import os, sys
from ui.ui_elements import *



################################################################################
# Globals
################################################################################
# variable for UI Object
app = None
# variable for CanSim Object
sim = None

pid_main= 0



################################################################################
# Functions
################################################################################    
def selectencryptionalgo():
    '''Function that will be called on algorithm selection'''
    selected = app.selected_algo.get()
    setencryptionalgo(selected)
    # Reset the array of encryption and decryption samples for the selected algorithm
    app.resetsamples(selected)
    # Set the description of the algorithm
    app.insertdescription(selected)



################################################################################
# Main
################################################################################
if __name__ == "__main__":
    # Pin the process to Core0, otherwise Scheduler will distribute it to other cores
    # Pin to core 0
    pid_main = os.getpid()
    os.sched_setaffinity(pid_main, {0})
    
    # Start the UI
    app = CANSimGUI()
    # Init the Sim environment
    sim = CanSim()

    #Initializa the CAN Bus
    sim.initializebus()

    # Set callbacks for Start/Stop Simulation in UI
    app.startsimcallback = sim.start_simulation
    app.stopsimcallback = sim.stop_simulation

    # Set command for crypto algorithm selection
    for eachbutton in app.rb_cryalgo_tab:
        eachbutton.config(command=selectencryptionalgo)
     
    # Call console printing functions
    app.printtosenderconsole()
    app.printtoreceiverconsole()

    #Run the application
    app.mainloop()

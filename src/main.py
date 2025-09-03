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



################################################################################
# Functions
################################################################################    
# This function sets the callback to be called by the simulation functions to
# print in the console
def setcallbackforconsoleprint(objcansim):
    for eachCanBus in objcansim.CanbusList:
        #Set callback for each Node in the Can bus
        for eachNode in eachCanBus.nodes:
            # Depeending on the type of Node
            if (NODE_SENDER == eachNode.nodetype):
                eachNode.consoleprint = app.printtosenderconsole
            else:
                eachNode.consoleprint = app.printtoreceiverconsole
 
#Function that will be called on algorithm selection               
def selectencryptionalgo():
    selected = app.selected_algo.get()
    setencryptionalgo(selected)
    # Set the description of the algorithm
    app.insertdescription(selected)



################################################################################
# Main
################################################################################
if __name__ == "__main__":
    # Start the UI
    app = CANSimGUI()
    # Init the Sim environment
    sim = CanSim()

    #Initializa the CAN Bus
    sim.initializebus()

    # Set callback for ConsolePrint
    setcallbackforconsoleprint(sim)

    # Set callbacks for Start/Stop Simulation in UI
    app.startsimcallback = sim.start_simulation
    app.stopsimcallback = sim.stop_simulation

    # Set command for crypto algorithm selection
    for eachbutton in app.rb_cryalgo_tab:
        eachbutton.config(command=selectencryptionalgo)

    #Run the application
    app.mainloop()

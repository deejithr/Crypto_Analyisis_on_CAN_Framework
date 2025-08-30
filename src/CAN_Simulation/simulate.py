"""
This module provides utility functions for CAN Network Simulation on Virtual bus.

It includes :
    * Classes for CAN Bus and CAN Nodes
    * Function to simulate the CAN Bus

"""
################################################################################
# Imports
################################################################################
import can
import threading
from typing import List
import time
from datetime import datetime as dt
from encrypt_decrypt.perform_encryption_decryption import *


################################################################################
# Macros
################################################################################
# Enums for Node Type
NODE_SENDER = 0
NODE_RECEIVER = 1

# Enum for Node States
NODE_DEINITIALIZED = 0
NODE_INITIALIZED = 1

# Delay
DELAY_20_MS = 20/1000


################################################################################
# Globals
################################################################################

# Global variable to indicate the CAN simulation state.
# Simulation will be stopped, once the state becomes False
simulationstate = False

################################################################################
# Classes
################################################################################
# Represents a CAN Message
class CANMessage:
    def __init__(self, canid, data, isextended):
        self.arbritration_id = canid
        self.data = data
        self.isextended = isextended

# Represents node in the Communication Bus
class Node:
    def __init__(self, nodename, nodetype, bus):
        self.nodename = nodename
        self.nodetype = nodetype
        self.nodebus = bus
        self.consoleprint = None

    # Function to create thread for the Node
    def createthread(self):
        # Create thread based on sender or Receiver
        try:
            if self.nodetype == NODE_SENDER:
                self.thread = threading.Thread(target=self.action_sender, args=())
            elif self.nodetype == NODE_RECEIVER:
                self.thread = threading.Thread(target=self.action_receiver, args=())
        except:
            print("[Error] Unable to create thread")
        
        #Start the Thread
        self.thread.start()

    # Function for actions to be performed by the Sender
    def action_sender(self):
        global simulationstate
        print("Sender Node: " + self.nodename +  " Initiated")
        self.nodestatus = NODE_INITIALIZED

        #Data bytes
        data = [0xAA, 0xBB, 0xCC, 0xDD, 0XEE, 0xFF, 0x00, 0x11]

        while True == simulationstate:
            try:
                #Perform Encryption
                encrypteddata = perform_encryption(data)
                
                # Create CAN Message
                can_msg = CANMessage(0xC0FFEE, encrypteddata, True)

                msg = can.Message(
                    arbitration_id=can_msg.arbritration_id,
                    data=can_msg.data,
                    is_extended_id=can_msg.isextended)
                
                self.nodebus.send(msg)
                # Send the message with a delay of 20ms
                time.sleep(DELAY_20_MS)
            except:
                print("[Error] Transmission error")

        print("Sender Node: " + self.nodename +  " de-initialized")
        self.nodestatus = NODE_DEINITIALIZED
        
    # Function for actions to be performed by the Receiver
    def action_receiver(self):
        global simulationstate
        print("Receiver Node: " + self.nodename +  " Initiated")
        self.nodestatus = NODE_INITIALIZED

        while True == simulationstate:
            try:
                received = self.nodebus.recv(1.0)  # timeout = 1s
                if received:
                    self.consoleprint(f"Received: {received}")
                    decrypteddata = perform_decryption(received.data)
            except:
                print("[Error] Reception error")

        print("Receiver Node: " + self.nodename + " de-initialized")
        self.nodestatus = NODE_DEINITIALIZED


# Represents a CAN Communication Bus
class CanBus:
    def __init__(self, busname):
        self.busname = busname
        # Create Virtual CAN Bus
        self.bus = can.interface.Bus(busname, bustype='socketcan', bitrate=250000)
        self.nodes : List[Node] = []
        
# Represents a CAN Simulation
class CanSim:
    def __init__(self):
        self.CanbusList: List[CanBus] = []

    #Function to Initialize the bus
    def initializebus(self):
        global objcanbus_1, objcanbus_2
        # Initialize CAN Bus
        objcanbus_1 = CanBus("vcan0")
        objcanbus_2 = CanBus("vcan0")

        #Add to the BusList
        self.CanbusList.append(objcanbus_1)
        self.CanbusList.append(objcanbus_2)

        #Instantiate the Nodes
        objcanbus_1.nodes.append(Node("ECU1", NODE_SENDER, objcanbus_1.bus))
        objcanbus_2.nodes.append(Node("ECU2", NODE_RECEIVER, objcanbus_2.bus))

    # This function starts the simulation
    def start_simulation(self):
        global simulationstate

        # Set the simulation State to TRUE
        simulationstate = True

        #Start each Node
        for eachBus in self.CanbusList:
            instantiatenodes(eachBus)

    # This function stops the simulation
    def stop_simulation(self):
        global simulationstate

        # Set Simulation State to False
        print(f"Stopping simulation... ")
        simulationstate = False

        # Wait for the nodes to be de-initialized
        while (
            NODE_DEINITIALIZED != self.CanbusList[0].nodes[0].nodestatus or
            NODE_DEINITIALIZED != self.CanbusList[1].nodes[0].nodestatus
        ):
            pass

        # # Once all the nodes are released, then close the CAN bus interface
        # print("Releasing the CAN bus Interface - " + self.CanbusList[0].busname)
        # self.CanbusList[0].bus.shutdown()
     
################################################################################
# Functions
################################################################################
# Function to start threads for each Node in the Can bus
def instantiatenodes(objbus):
    for eachNode in objbus.nodes:
        eachNode.createthread()



    
    

    


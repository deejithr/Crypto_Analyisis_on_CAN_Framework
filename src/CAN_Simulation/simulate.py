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
DELAY_IN_S = 20/1000

#Loop Timeout seconds
looptimeout = 2

################################################################################
# Globals
################################################################################

# Global variable to indicate the CAN simulation state.
# Simulation will stop, once the state becomes False
simulationstate = False

#Global variable for CAN Message
can_msg = None

# For deadlne miss measurements
deadlinemisscounts = 0
sentmessagescount = 0 

################################################################################
# Classes
################################################################################
class CANMessage:
    '''Represents a CAN Message'''
    def __init__(self, canid, data, isextended):
        self.arbritration_id = canid
        self.data = data
        self.isextended = isextended

class Node:
    '''Represents node in the Communication Bus'''
    def __init__(self, nodename, nodetype, bus):
        self.nodename = nodename
        self.nodetype = nodetype
        self.nodebus = bus
        self.consoleprint = None

    def createthread(self):
        '''Function to create thread for the Node'''
        # Create thread based on node type
        try:
            if self.nodetype == NODE_SENDER:
                self.thread = threading.Thread(target=self.action_sender, args=())
            elif self.nodetype == NODE_RECEIVER:
                self.thread = threading.Thread(target=self.action_receiver, args=())
        except:
            print("[Error] Unable to create thread")
        
        #Start the thread
        self.thread.start()

    def action_sender(self):
        '''Function for actions to be performed by the sender'''
        global simulationstate, encrypt_samples, can_msg, DELAY_IN_S
        global deadlinemisscounts, sentmessagescount

        print("Sender Node: " + self.nodename +  " Initiated")
        self.nodestatus = NODE_INITIALIZED
        
        # Pin the thread to Core0, otherwise Scheduler will distribute it to other cores
        # Pin to core 0
        pid = threading.get_native_id()
        os.sched_setaffinity(pid, {0})

        #For deadlinemiss counts
        deadlinemisscounts = 0
        sentmessagescount = 0

        next_execution_ns = prev = time.perf_counter_ns()

        while True == simulationstate:
            try:
                # Perform Encryption
                encrypteddata, encryptiontime = perform_encryption(can_msg.data)
                print("Sender: Data before Encryption:  " + str(can_msg.data))

                msg = can.Message(
                    arbitration_id=can_msg.arbritration_id,
                    data=encrypteddata,
                    is_extended_id=can_msg.isextended)
                
                msg.timestamp = time.time()
                self.nodebus.send(msg)
                # Increment the count of sent messages
                sentmessagescount +=1
                self.consoleprint(f"Sent: {msg}    t_encrypt: {encryptiontime:.3f} us")

                # Get the current timestamp
                now = time.perf_counter_ns()
                deadline = next_execution_ns + int(DELAY_IN_S * CONVERT_S_TO_NS)

                print("Period: ", (now - prev) * CONVERT_NS_TO_MS)
                # Update Prev with now value
                prev = now

                if now > deadline:
                    deadlinemisscounts += 1
                    print("Deadline missed : ", deadlinemisscounts)

                # Next Execution Window
                next_execution_ns += int(DELAY_IN_S * CONVERT_S_TO_NS)

                # to send the message with the configured delay, Calculate how long to sleep
                time_to_sleep_ns = next_execution_ns - time.perf_counter_ns()
                if time_to_sleep_ns > 0:
                    print("Sleep time: " ,  time_to_sleep_ns * CONVERT_NS_TO_MS)
                    # Provide the calculated sleep time
                    time.sleep(time_to_sleep_ns * CONVERT_NS_TO_S)
            except:
                print("[Error] Transmission error")

        print("Sender Node: " + self.nodename +  " de-initialized")
        self.nodestatus = NODE_DEINITIALIZED
        
    def action_receiver(self):
        '''Function for actions to be performed by the Receiver'''
        global simulationstate, decrypt_samples
        print("Receiver Node: " + self.nodename +  " Initiated")
        self.nodestatus = NODE_INITIALIZED

        decrypt_samples = []
        # Pin the thread to Core0, otherwise Scheduler will distribute it to other cores
        # Pin to core 0
        pid = threading.get_native_id()
        os.sched_setaffinity(pid, {0})  

        while True == simulationstate:
            try:
                received = self.nodebus.recv(1.0)  # timeout = 1s
                if received:
                    # Perform Decrytpion and acceptance
                    decrypteddata, decryptiontime, accepted = perform_decryption(received.data)
                    print("Receiver: Data after Decryption:   " + str(list(decrypteddata)))
                    self.consoleprint(f"Received: {received}    t_decrypt: {decryptiontime:.3f} us", accepted)
            except:
                print("[Error] Reception error")

        print("Receiver Node: " + self.nodename + " de-initialized")
        self.nodestatus = NODE_DEINITIALIZED


class CanBus:
    def __init__(self, busname):
        '''Represents a CAN Communication Bus'''
        self.busname = busname
        # Create Virtual CAN Bus
        self.bus = can.interface.Bus(busname, bustype='socketcan', bitrate=250000,
                                      preserve_timestamps=True)
        self.nodes : List[Node] = []
        
class CanSim:
    '''Represents a CAN Simulation'''
    def __init__(self):
        self.CanbusList: List[CanBus] = []

    def initializebus(self):
        '''Function to Initialize the bus'''
        global objcanbus_1, objcanbus_2
        # Initialize CAN Bus
        objcanbus_1 = CanBus("vcan0")
        objcanbus_2 = CanBus("vcan0")

        #Add Canbus to the Simulation BusList
        self.CanbusList.append(objcanbus_1)
        self.CanbusList.append(objcanbus_2)

        #Instantiate the Nodes
        objcanbus_1.nodes.append(Node("ECU1", NODE_SENDER, objcanbus_1.bus))
        objcanbus_2.nodes.append(Node("ECU2", NODE_RECEIVER, objcanbus_2.bus))

    def start_simulation(self):
        '''This function starts the simulation'''
        global simulationstate

        # Set the simulation State to TRUE
        simulationstate = True

        #Start each Node
        for eachBus in self.CanbusList:
            instantiatenodes(eachBus)

    
    def stop_simulation(self):
        '''This function stops the simulation'''
        global simulationstate

        # Set Simulation State to False
        print(f"Stopping simulation... ")
        simulationstate = False

        # Wait for the nodes to be de-initialized or until timeout elapsed
        loopstarttime = time.time()
        while ((
            NODE_DEINITIALIZED != self.CanbusList[0].nodes[0].nodestatus or
            NODE_DEINITIALIZED != self.CanbusList[1].nodes[0].nodestatus
        ) and
        ((time.time() - loopstarttime < looptimeout))):
            pass


################################################################################
# Functions
################################################################################
def instantiatenodes(objbus):
    '''Function to start threads for each Node in the Can bus'''
    for eachNode in objbus.nodes:
        eachNode.createthread()

def setcanmessage(canid, data, isExtended):
    '''Function sets the parameters for CAN Message'''
    global can_msg
    can_msg = CANMessage(canid, data, isExtended)

def setmsgperiodicity(period):
    '''Function sets the periodicity of CAN Message'''
    global DELAY_IN_S
    DELAY_IN_S = period/1000

def getdeadlinemissratio():
    global deadlinemisscounts, sentmessagescount
    return (100 * (deadlinemisscounts)/sentmessagescount)



    
    

    


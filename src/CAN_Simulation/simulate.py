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

# To enable debug prints in the file
DEBUG_PRINT = True

# Delay
DELAY_IN_S = 20/1000

#Loop Timeout in seconds
LOOPTIMEOUT = 2

################################################################################
# Globals
################################################################################
#Global variable for CAN Message
can_msg = None

#Process Ids for sender and receiver
pid_sender = 0
pid_receiver = 0

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
        self.nodestatus = NODE_DEINITIALIZED

    def createprocess(self, console_queue, 
                      simstate,
                      deadlinemc,
                      sentmsgc,
                      crypt_samples, 
                      crypt_cpuper,
                      encscheme_state,
                      benchmarkinprogress
                      ):
        '''Function to create process for the Node'''
        # Create process based on node type
        try:
            if self.nodetype == NODE_SENDER:
                self.process = multiprocessing.Process(target=self.action_sender, args=(console_queue,
                                                                                        simstate, 
                                                                                        deadlinemc, 
                                                                                        sentmsgc,
                                                                                        crypt_samples, 
                                                                                        crypt_cpuper,
                                                                                        encscheme_state,
                                                                                        benchmarkinprogress
                                                                                        ))
            elif self.nodetype == NODE_RECEIVER:
                self.process =  multiprocessing.Process(target=self.action_receiver, args=(console_queue,
                                                                                           simstate,
                                                                                           crypt_samples, 
                                                                                           crypt_cpuper,
                                                                                           encscheme_state,
                                                                                           benchmarkinprogress
                                                                                        ))
        except Exception as e:
            print("[Error] Unable to create process {e}")
            import traceback
            traceback.print_exc()
        
        #Start the thread
        self.process.start()



    def action_sender(self, console_queue, 
                      simulationstate, 
                      deadlinemisscounts, 
                      sentmessagescount,
                      encrypt_samples, encrypt_cpuper,
                      encscheme_state,
                      benchmarkinprogress
                      ):
        '''Function for actions to be performed by the sender'''
        global can_msg, DELAY_IN_S
        global pid_sender

        print("Sender Node: " + self.nodename +  " Initiated")
        self.nodestatus = NODE_INITIALIZED
        
        # Pin the thread to Core1, otherwise Scheduler will distribute it to other cores
        # Pin to core 1
        pid_sender = os.getpid()
        os.sched_setaffinity(pid_sender, {1})

        # For deadlinemiss counts
        # Reset the deadline miss counts
        deadlinemisscounts.value = 0
        sentmessagescount.value = 0

        next_execution_ns = prev = 0
        firstCall = True

        while True == simulationstate.value:
            try:
                #if Performing benchmark, stop after 200 messages
                if((True == benchmarkinprogress) and
                   (200 >= sentmessagescount.value)):
                    # Perform Encryption
                    encrypteddata, encryptiontime = perform_encryption(can_msg.data, 
                                                                       encrypt_samples, 
                                                                       encrypt_cpuper,
                                                                       encscheme_state,
                                                                       can_msg.arbritration_id,
                                                                       can_msg.isextended
                                                                       )
                    print("Sender: Data before Encryption:  " + str(can_msg.data))

                    msg = can.Message(
                        arbitration_id=can_msg.arbritration_id,
                        data=encrypteddata,
                        is_extended_id=can_msg.isextended,
                        is_rx = False)

                    msg.timestamp = time.time()
                    self.nodebus.send(msg)
                    # Increment the count of sent messages
                    sentmessagescount.value +=1
                    console_queue.put(f"Sent: {msg}    t_encrypt: {encryptiontime:.3f} us")
                    print("action_sender: sentmessagescount = ", sentmessagescount.value)

                    # Get the current timestamp
                    now = time.perf_counter_ns()
                    if(True == firstCall):
                        next_execution_ns = prev = time.perf_counter_ns()
                    deadline = next_execution_ns + int(DELAY_IN_S * CONVERT_S_TO_NS)

                    if(True == firstCall):
                        time.sleep(DELAY_IN_S)
                        firstCall = False
                    else:
                        if (True == DEBUG_PRINT):
                            print("Period: ", (now - prev) * CONVERT_NS_TO_MS)
                            print("now : ", now)
                            print("deadline : ", deadline)

                        # Consider Deadline missed, only if the value exceeds more 
                        # than 1ms from the period
                        if ((now > deadline) and
                            (now - deadline) > 2000000):
                            deadlinemisscounts.value += 1
                            if (True == DEBUG_PRINT):
                                print("Deadline missed counts : ", deadlinemisscounts.value)

                        # Next Execution Window
                        next_execution_ns += int(DELAY_IN_S * CONVERT_S_TO_NS)
                        prev = now

                        # to send the message with the configured delay, Calculate how long to sleep
                        time_to_sleep_ns = next_execution_ns - time.perf_counter_ns()
                        if time_to_sleep_ns > 0:
                            if (True == DEBUG_PRINT):
                                print("Sleep time: " ,  time_to_sleep_ns * CONVERT_NS_TO_MS)
                            # Provide the calculated sleep time
                            time.sleep(time_to_sleep_ns * CONVERT_NS_TO_S)
            except Exception as e:
                print("[Error] Transmission error. {e}")
                import traceback
                traceback.print_exc()

        print("Sender Node: " + self.nodename +  " de-initialized")
        self.nodestatus = NODE_DEINITIALIZED
        
    def action_receiver(self, console_queue, simulationstate, decrypt_samples, decrypt_cpuper,
                        encscheme_state, benchmarkinprogress
                        ):
        '''Function for actions to be performed by the Receiver'''
        global pid_receiver
        print("Receiver Node: " + self.nodename +  " Initiated")
        self.nodestatus = NODE_INITIALIZED

        # Pin the thread to Core2, otherwise Scheduler will distribute it to other cores
        # Pin to core 2
        pid_receiver = os.getpid()
        os.sched_setaffinity(pid_receiver, {2})  

        while True == simulationstate.value:
            try:
                # received = self.nodebus.recv()
                for received in self.nodebus:
                    # Setting the received flag to True
                    received.is_rx = True
                    # Perform Decrytpion and acceptance
                    decrypteddata, decryptiontime, accepted = perform_decryption(received.data,
                                                                                 decrypt_samples, 
                                                                                 decrypt_cpuper,
                                                                                 encscheme_state,
                                                                                 received.arbitration_id,
                                                                                 received.is_extended_id
                                                                                 )
                    acceptancestate = "  ✅" if DECRYPT_OK == accepted else "  ❌"
                    print("Receiver: Data after Decryption:   " + str(list(decrypteddata)))
                    console_queue.put(f"Received: {received}    t_decrypt: {decryptiontime:.3f} us {acceptancestate}")
            except Exception as e:
                print("[Error] Reception error {e}")
                import traceback
                traceback.print_exc()

        print("Receiver Node: " + self.nodename + " de-initialized")
        self.nodestatus = NODE_DEINITIALIZED


class CanBus:
    def __init__(self, busname):
        '''Represents a CAN Communication Bus'''
        self.busname = busname
        # Create Virtual CAN Bus
        self.bus = can.ThreadSafeBus(busname, interface='socketcan', bitrate=250000,
                                      preserve_timestamps=True, receive_own_messages=True)
        self.nodes : List[Node] = []
        
class CanSim:
    '''Represents a CAN Simulation'''
    def __init__(self):
        self.CanbusList: List[CanBus] = []

    def initializebus(self):
        '''Function to Initialize the bus'''
        global objcanbus_1
        # Initialize CAN Bus
        objcanbus_1 = CanBus("vcan0")

        #Add Canbus to the Simulation BusList
        self.CanbusList.append(objcanbus_1)

        #Instantiate the Nodes
        objcanbus_1.nodes.append(Node("ECU1", NODE_SENDER, objcanbus_1.bus))
        objcanbus_1.nodes.append(Node("ECU2", NODE_RECEIVER, objcanbus_1.bus))

    def start_simulation(self, ui_senderqueue, ui_receiverqueue, 
                         simulationstate, deadlinemisscounts, sentmessagescount,
                         encrypt_samples, encrypt_cpuper,
                         decrypt_samples, decrypt_cpuper,
                         encscheme_state,
                         benchmarkinprogress):
        '''This function starts the simulation'''

        # Set the simulation State to TRUE
        simulationstate.value = True

        #Start each Node
        for eachBus in self.CanbusList:
            instantiatenodes(eachBus, ui_senderqueue, ui_receiverqueue, 
                             simulationstate, deadlinemisscounts, sentmessagescount,
                             encrypt_samples, encrypt_cpuper,
                             decrypt_samples, decrypt_cpuper,
                             encscheme_state,
                             benchmarkinprogress)

    
    def stop_simulation(self, simulationstate):
        '''This function stops the simulation'''
        # Set Simulation State to False
        print(f"Stopping simulation... ")
        simulationstate.value = False

        # Wait for the nodes to be de-initialized or until timeout elapsed
        loopstarttime = time.time()
        while ((
            NODE_DEINITIALIZED != self.CanbusList[0].nodes[0].nodestatus or
            NODE_DEINITIALIZED != self.CanbusList[0].nodes[1].nodestatus
        ) and
        ((time.time() - loopstarttime < LOOPTIMEOUT))):
            pass

        #If the sender or receiver process is stil alive, terminate them
        if(self.CanbusList[0].nodes[0].process.is_alive()):
            self.CanbusList[0].nodes[0].process.terminate()
            print("stop_simulation: Sender Node Stopped")
        if(self.CanbusList[0].nodes[1].process.is_alive()):
            self.CanbusList[0].nodes[1].process.terminate()
            print("stop_simulation: Receiver Node Stopped")
        


################################################################################
# Functions
################################################################################
def instantiatenodes(objbus, squeue, rqueue, simstate, deadlinemc, 
                     sentmsgc, encrypt_samples, encrypt_cpuper, 
                     decrypt_samples, decrypt_cpuper,
                     encscheme_state, benchmarkinprogress):
    '''Function to start threads for each Node in the Can bus'''
    for eachNode in objbus.nodes:
        #Check the Node type
        if(NODE_SENDER == eachNode.nodetype):
            eachNode.createprocess(squeue, simstate, deadlinemc, sentmsgc, encrypt_samples, encrypt_cpuper,
                                   encscheme_state, benchmarkinprogress)
        else:
            eachNode.createprocess(rqueue, simstate, None, None, decrypt_samples, decrypt_cpuper,
                                   encscheme_state, None)

def setcanmessage(canid, data, isExtended):
    '''Function sets the parameters for CAN Message'''
    global can_msg
    can_msg = CANMessage(canid, data, isExtended)

def setmsgperiodicity(period):
    '''Function sets the periodicity of CAN Message'''
    global DELAY_IN_S
    DELAY_IN_S = period/1000




    
    

    


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
import binascii
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
DEBUG_PRINT = False

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
                      benchmarkinprogress,
                      ready_event,
                      replay_sim_state
                      ):
        '''Function to create process for the Node'''
        # Create process based on node type
        try:
            if self.nodetype == NODE_SENDER:
                self.process = multiprocessing.Process(target=self.action_sender, 
                                                       args=(console_queue,
                                                       simstate, 
                                                       deadlinemc, 
                                                       sentmsgc,
                                                       crypt_samples, 
                                                       crypt_cpuper,
                                                       encscheme_state,
                                                       benchmarkinprogress,
                                                       ready_event,
                                                       replay_sim_state
                                                       ))
            elif self.nodetype == NODE_RECEIVER:
                self.process =  multiprocessing.Process(target=self.action_receiver, 
                                                        args=(console_queue,
                                                              simstate,
                                                              crypt_samples, 
                                                              crypt_cpuper,
                                                              encscheme_state,
                                                              benchmarkinprogress,
                                                              ready_event,
                                                              replay_sim_state
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
                      benchmarkinprogress, 
                      ready_event,
                      replay_sim_state
                      ):
        '''Function for actions to be performed by the sender'''
        global can_msg, DELAY_IN_S
        global pid_sender

        print("Sender Node: " + self.nodename +  " Initiated")
        self.nodestatus = NODE_INITIALIZED
        
        # Pin the thread to Core1, otherwise Scheduler will distribute it to other cores
        # Pin to core 1
        pid_sender = os.getpid()
        p = psutil.Process(pid_sender)
        p.cpu_affinity([1])

        #Open the file for saving the CAN frames in case of Replay Attack Simulation
        if(2 == replay_sim_state.value):
            fp = open("CAN_Frames_Saved.txt", "w")

        #If replay sim state is in REPLAYSIM_REPLAY_FRAMES
        if(4 == replay_sim_state.value):
            fp = open("CAN_Frames_Saved.txt", "r")
            CANFrames = fp.readlines()

        # For deadlinemiss counts
        # Reset the deadline miss counts
        deadlinemisscounts.value = 0
        sentmessagescount.value = 0

        next_execution_ns = prev = 0
        firstCall = True

        while True == simulationstate.value:
            try:
                if(
                   #Continue normally, if no benchmark in progress
                   (False == benchmarkinprogress) or
                   #if Performing benchmark, stop after BENCHMARK_MESSAGE_COUNT messages
                   ((True == benchmarkinprogress) and
                   (BENCHMARK_MESSAGE_COUNT > sentmessagescount.value))
                   ):
                    
                    #Check if state is in REPLAYSIM_REPLAY_FRAMES
                    if(4 != replay_sim_state.value):
                        # Get the current timestamp
                        now = time.perf_counter_ns()
                        if(True == firstCall):
                            next_execution_ns = prev = time.perf_counter_ns()
                        deadline = next_execution_ns + int(DELAY_IN_S * CONVERT_S_TO_NS)

                        if(True != firstCall):
                            # Consider Deadline missed, only if the value exceeds more 
                            # than 2ms (tolerance) from the period
                            if ((now > deadline) and
                                (now - deadline) > 2000000):
                                deadlinemisscounts.value += 1
                                if (True == DEBUG_PRINT):
                                    print("Deadline missed counts : ", deadlinemisscounts.value)

                        # Perform Encryption
                        encrypteddata, encryptiontime = perform_encryption(can_msg.data, 
                                                                           encrypt_samples, 
                                                                           encrypt_cpuper,
                                                                           encscheme_state,
                                                                           can_msg.arbritration_id,
                                                                           can_msg.isextended,
                                                                           ready_event
                                                                           )
                        # With encryption scheme, only 6 data bytes are send, 2 bytes will be 
                        # truncated MAC
                        if(True == encscheme_state.get()):
                            print("Sender: Data before Encryption:  " + str(can_msg.data[0:6]))
                        else:
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

                        # If recording frames for replay attack is On
                        if(2 == replay_sim_state.value):
                            if(REPLAY_MESSAGE_COUNT > sentmessagescount.value):
                                data_hex = binascii.hexlify(msg.data).decode('utf-8').upper()
                                fp.write(data_hex + "\n")
                            else:
                                #Stop recording once the message count reaches REPLAY_MESSAGE_COUNT
                                fp.close()

                        if(True == firstCall):
                            time.sleep(DELAY_IN_S)
                            firstCall = False
                        else:
                            if (True == DEBUG_PRINT):
                                print("Period: " + str((now - prev) * CONVERT_NS_TO_MS) + " ms")
                                print("now : ", now)
                                print("deadline : ", deadline)

                            # Next Execution Window
                            next_execution_ns += int(DELAY_IN_S * CONVERT_S_TO_NS)
                            prev = now

                            # to send the message with the configured delay, Calculate how long to 
                            # sleep
                            time_to_sleep_ns = next_execution_ns - time.perf_counter_ns()
                            if time_to_sleep_ns > 0:
                                # sleep value should never exceed the periodicity configured
                                time_to_sleep_ns = time_to_sleep_ns \
                                    if (time_to_sleep_ns < (DELAY_IN_S * CONVERT_S_TO_NS))\
                                    else (DELAY_IN_S * CONVERT_S_TO_NS)
                                if (True == DEBUG_PRINT):
                                    print("Sleep time: " ,  time_to_sleep_ns * CONVERT_NS_TO_MS)
                                # Provide the calculated sleep time
                                time.sleep(truncate_float(time_to_sleep_ns * CONVERT_NS_TO_S, 2))
                    
                    # If replay of frames in progress for Replay attack simulation
                    elif(4 == replay_sim_state.value):
                        #Increment the sentmessagescount
                        sentmessagescount.value += 1
                        if(sentmessagescount.value <= len(CANFrames)):
                            data = binascii.unhexlify(CANFrames[sentmessagescount.value - 1].replace("\n",""))
                            #Frame the message 
                            msg = can.Message(
                            arbitration_id=can_msg.arbritration_id,
                            data=data,
                            is_extended_id=can_msg.isextended,
                            is_rx = False)

                            msg.timestamp = time.time()
                            #Send the CAN message
                            self.nodebus.send(msg)

                            # Sleep until next periodicity
                            time.sleep(DELAY_IN_S)


            except Exception as e:
                print("[Error] Transmission error. {e}")
                import traceback
                traceback.print_exc()


        print("Sender Node: " + self.nodename +  " de-initialized")
        self.nodestatus = NODE_DEINITIALIZED
        
    def action_receiver(self, console_queue, simulationstate, decrypt_samples, decrypt_cpuper,
                        encscheme_state, benchmarkinprogress, ready_event, replay_sim_state
                        ):
        '''Function for actions to be performed by the Receiver'''
        global pid_receiver
        print("Receiver Node: " + self.nodename +  " Initiated")
        self.nodestatus = NODE_INITIALIZED

        # Flag to indicate that the receiver is ready or not
        receiver_ready = False

        # Pin the thread to Core2, otherwise Scheduler will distribute it to other cores
        # Pin to core 2
        pid_receiver = os.getpid()
        p = psutil.Process(pid_receiver)
        p.cpu_affinity([2])  

        while True == simulationstate.value:
            try:
                received = None
                received = self.nodebus.recv(timeout=0.005)
                if received is not None:
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
                    if(False == receiver_ready):
                        #Indicate the reciever is ready
                        ready_event.set()
                        receiver_ready = True
                        print("Receiver Node: " + self.nodename +  " Ready")
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
                         benchmarkinprogress,
                         ready_event,
                         replay_sim_state):
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
                             benchmarkinprogress,
                             ready_event,
                             replay_sim_state)

    
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

        #If the sender or receiver process is still alive, terminate them
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
                     encscheme_state, benchmarkinprogress, ready_event, replay_sim_state):
    '''Function to start threads for each Node in the Can bus'''
    for eachNode in objbus.nodes:
        #Check the Node type
        if(NODE_SENDER == eachNode.nodetype):
            eachNode.createprocess(squeue, simstate, deadlinemc, sentmsgc, encrypt_samples, encrypt_cpuper,
                                   encscheme_state, benchmarkinprogress, ready_event, replay_sim_state)
        else:
            eachNode.createprocess(rqueue, simstate, None, None, decrypt_samples, decrypt_cpuper,
                                   encscheme_state, None, ready_event, None)

def setcanmessage(canid, data, isExtended):
    '''Function sets the parameters for CAN Message'''
    global can_msg
    can_msg = CANMessage(canid, data, isExtended)

def setmsgperiodicity(period):
    '''Function sets the periodicity of CAN Message'''
    global DELAY_IN_S
    DELAY_IN_S = period/1000

def truncate_float(f, decimal_places):
    """Truncates a float to a specified number of decimal places."""
    multiplier = 10 ** decimal_places
    return int(f * multiplier) / multiplier




    
    

    


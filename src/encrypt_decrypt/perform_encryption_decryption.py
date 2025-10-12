"""
This module provides utility functions for encryption and decryption based on 
the algorithm selected.

It includes :
    * Function to perform encryption/decryption of data

"""
################################################################################
# Imports
################################################################################
import statistics
import time
from Crypto_Algorithms.RC4 import *
from Crypto_Algorithms.SPECK import *
from Crypto_Algorithms.PRESENT import *
import numpy as np
import psutil, os
import multiprocessing
from multiprocessing import Process, Value, Manager
from icecream import ic



################################################################################
# Macros
################################################################################
# cpu frequency for calculating the cpu cycles required per byte
# this value has been fetched from cpuinfo file in process
#cat /proc/cpuinfo | grep "MHz"
CPU_FREQ_MHZ = 2592.008

# Enums for Can message accepted or not
DECRYPT_OK = 0
DECRYPT_NOT_OK = 1

# Conversion Macros
CONVERT_S_TO_NS = 1_000_000_000
CONVERT_NS_TO_S = 1/ 1_000_000_000
CONVERT_NS_TO_MS = 1/ 1_000_000

#Encryption Algorithms
ENCRYPTION_ALGORITHMS = ["None", "RC4", "SPECK", "TEA", "PRESENT", "AES128" ]

################################################################################
# Globals
################################################################################
# Global Variable to store Encryption Algorithm
g_encryptionalgo = "None"

#Encryption Class Object
g_encryption = None

################################################################################
# Functions
################################################################################
def perform_encryption(data, encrypt_samples, encrypt_cpuper):
    ''' Perfrom encryption using the selected Algorithm'''
    # Start Measurement
    encryptiontime = 0
    processid = psutil.Process(os.getpid())
    # For Cpu Percentage Calculation. Initial call of cpu_percent is for setting the baseline
    cpupercent_b = processid.cpu_percent(interval=None)
    encryptionstarttime = time.perf_counter_ns()
    
    #Implementation pending for other algorithms
    # Call encryption function depending on the algorithm
    # to get the encrypted data
    if("RC4" == g_encryptionalgo):
        data = g_encryption.rc4encrypt(data, len(data))
    elif("SPECK" == g_encryptionalgo):
        data = g_encryption.speckencrypt(data)
    elif("PRESENT" == g_encryptionalgo):
        data = g_encryption.presentencrypt(data)
    else:
        pass
    
    # Stop Measurement
    encryptionendtime = time.perf_counter_ns()
    # Get the cpu percentage
    cpupercent_a = processid.cpu_percent(interval=None)
    
    # Storing the encryption cpu percent into the encrypt_cpuper shared variables
    enccpupers = encrypt_cpuper[g_encryptionalgo]
    enccpupers.append((cpupercent_a)/psutil.cpu_count())
    encrypt_cpuper[g_encryptionalgo] = enccpupers
    
    #Time taken for encryption
    encryptiontime = (encryptionendtime - encryptionstarttime) / us_DURATION
    
    # Storing the encryption times into the encrypt_samples shared variables
    enctimes = encrypt_samples[g_encryptionalgo]
    enctimes.append(encryptiontime)
    encrypt_samples[g_encryptionalgo] = enctimes

    
    return data, encryptiontime

def isMessageAccepted(data):
    # Implmentation Pending
    return DECRYPT_OK


def perform_decryption(data, decrypt_samples, decrypt_cpuper):
    '''Perform Decryption using the selected Algorithm'''
    accepted = DECRYPT_NOT_OK
    
    # Start Measurement
    decryptiontime = 0
    # For Cpu Percentage Calculation. Initial call of cpu_percent is for setting the baseline
    processid = psutil.Process(os.getpid())
    cpupercent_b =processid.cpu_percent(interval=None)
    decryptionstarttime = time.perf_counter_ns()

    #If encryption Mechanism enabled, do decrytpion only if the message is accepted
    if(DECRYPT_OK == isMessageAccepted(data)):
        accepted = DECRYPT_OK
        #Implementation pending for other algorithms
        # Call decrytion function depending on the algorithm
        # to decrypt the data
        if("RC4" == g_encryptionalgo):
            data = g_encryption.rc4decrypt(data, len(data))
        elif("SPECK" == g_encryptionalgo):
            data = g_encryption.speckdecrypt(data)
        elif("PRESENT" == g_encryptionalgo):
            data = g_encryption.presentdecrypt(data)
        else:
            pass
    # End Measurement
    decryptionendtime = time.perf_counter_ns()
    # Get the CPU Percentage
    cpupercent_a = processid.cpu_percent(interval=None)

    # Storing the decryption cpu percent into the decrypt_cpuper shared variables
    decpupers = decrypt_cpuper[g_encryptionalgo]
    decpupers.append((cpupercent_a)/psutil.cpu_count())
    decrypt_cpuper[g_encryptionalgo] = decpupers

    #Time taken for decryption
    decryptiontime = (decryptionendtime - decryptionstarttime) / us_DURATION
    
    # Storing the encryption times into the encrypt_samples shared variables
    dectimes = decrypt_samples[g_encryptionalgo]
    dectimes.append(decryptiontime)
    decrypt_samples[g_encryptionalgo] = dectimes

    return data, decryptiontime, accepted

def setencryptionalgo(algorithm):
    '''Callback called on selecting the encyrption algorithm'''
    global g_encryptionalgo, g_encryption
    
    # Set the selected algorithm to the global variable
    g_encryptionalgo = algorithm

    if ("RC4" == g_encryptionalgo):
        g_encryption = RC4(RC4_KEY, RC4_S_ARRAY_SIZE)
    elif ("SPECK" == g_encryptionalgo):
        g_encryption = SPECK(SPECK_KEY)
    elif ("PRESENT" == g_encryptionalgo):
        g_encryption = PRESENT()
    else:
        pass
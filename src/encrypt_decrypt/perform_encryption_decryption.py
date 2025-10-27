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
from Crypto_Algorithms.xTEA import *
from Crypto_Algorithms.AES import *
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
ENCRYPTION_ALGORITHMS = ["None", "RC4", "SPECK", "xTEA", "PRESENT", "AES128", "ENCRYPTION_SCHEME" ]

################################################################################
# Globals
################################################################################
# Global Variable to store Encryption Algorithm
g_encryptionalgo = "None"

#Encryption Class Object
g_encryption = None

#Global objects for Encryption Scheme
g_noncecreation = None
g_keystreamgen = None
g_macgeneration = None

g_noncealgo = None
g_keystreamalgo = None 
g_macgenalgo = None

g_canid = 0

g_sendercounter = {}
g_receivercounter = {}

sender_processid = 0
receiver_processid = 0

################################################################################
# Functions
################################################################################
def encrypt(algo, encobj, data): 
    '''Function to encrypt data based on the algorithm'''
    if("RC4" == algo):
        data = encobj.rc4encrypt(data)
    elif("SPECK" == algo):
        data = encobj.speckencrypt(data)
    elif("PRESENT" == algo):
        data = encobj.presentencrypt(data)
    elif("xTEA" == algo):
        data = encobj.encrypt_xtea(data)
    elif("AES128" == algo):
        data = encobj.aesencrypt(data)
    else:
        pass
    return data

def decrypt(algo, encobj, data): 
    '''Function to decrypt data based on the algorithm'''
    if("RC4" == algo):
        data = encobj.rc4decrypt(data)
    elif("SPECK" == algo):
        data = encobj.speckdecrypt(data)
    elif("PRESENT" == algo):
        data = encobj.presentdecrypt(data)
    elif("xTEA" == algo):
        data = encobj.decrypt_xtea(data)
    elif("AES128" == algo):
        data = encobj.aesdecrypt(data)
    else:
        pass
    return data

def encryption_scheme_encrypt(data):
    global g_canid, g_keystreamgen, g_noncecreation, g_macgeneration
    global g_noncealgo, g_keystreamalgo, g_macgenalgo
    
    #Get the counter 
    if(g_canid not in g_sendercounter.keys()):
        g_sendercounter[g_canid] = 0
    
    #Append the counter and CANID to create input for Nonce creation
    nonceinput = g_canid.to_bytes(4,'big') + g_sendercounter[g_canid].to_bytes(4,'big')
    #Encrypt this Nonce using Nonce-encrytpion Algorithm
    Nonce = encrypt(g_noncealgo, g_noncecreation, nonceinput)
    # Generate Keystream with this Nonce
    S = encrypt(g_keystreamalgo, g_keystreamgen, Nonce)
    #Encrypted Payload
    for byte_a, byte_b in zip(data, S):
        C = byte_a ^ byte_b

    #Increment the counter 
    g_sendercounter[g_canid] += 1

    #Perform MAC generation
    return C

def perform_encryption(data, encrypt_samples, encrypt_cpuper,
                       encscheme_state, canid, isextended
                       ):
    ''' Perfrom encryption using the selected Algorithm'''
    global sender_processid
    # Start Measurement
    encryptiontime = 0
    sender_processid = psutil.Process(os.getpid())
    # For Cpu Percentage Calculation. Initial call of cpu_percent is for setting the baseline
    cpupercent_b = sender_processid.cpu_percent(interval=None)
    encryptionstarttime = time.perf_counter_ns()
    
    #Implementation pending for other algorithms
    # Call encryption function depending on the algorithm
    # to get the encrypted data
    
    # if Encryption Scheme enabled
    if(True == encscheme_state.get()):
        data = encryption_scheme_encrypt(data)
    else:
        data = encrypt(g_encryptionalgo, g_encryption, data)
    
    # Stop Measurement
    encryptionendtime = time.perf_counter_ns()
    # Get the cpu percentage
    cpupercent_a = sender_processid.cpu_percent(interval=None)
    
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


def perform_decryption(data, decrypt_samples, decrypt_cpuper,
                       encscheme_state, canid, isextended
                       ):
    '''Perform Decryption using the selected Algorithm'''
    global receiver_processid
    accepted = DECRYPT_NOT_OK
    
    # Start Measurement
    decryptiontime = 0
    # For Cpu Percentage Calculation. Initial call of cpu_percent is for setting the baseline
    receiver_processid = psutil.Process(os.getpid())
    decryptionstarttime = time.perf_counter_ns()
    # For Cpu Percentage Calculation. Initial call of cpu_percent is for setting the baseline
    cpupercent_b = receiver_processid.cpu_percent(interval=None)

    #If encryption Mechanism enabled, do decrytpion only if the message is accepted
    if(DECRYPT_OK == isMessageAccepted(data)):
        accepted = DECRYPT_OK
        #Implementation pending for other algorithms
        # Call decrytion function depending on the algorithm
        # to decrypt the data
        # Check if Encryption Scheme enabled
        if(True == encscheme_state.get()):
            data = encryption_scheme_decrypt(data)
        else:
            data = decrypt(g_encryptionalgo, g_encryption, data)
    
    # End Measurement
    decryptionendtime = time.perf_counter_ns()
    # Get the CPU Percentage
    cpupercent_a = receiver_processid.cpu_percent(interval=None)

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

def initencryptionobject(algo):
    '''Initialize the encryption Object based on the algorithm passed'''
    encobj = None
    if ("RC4" == algo):
        encobj = RC4(RC4_KEY, RC4_S_ARRAY_SIZE)
    elif ("SPECK" == algo):
        encobj = SPECK(SPECK_KEY)
    elif ("PRESENT" == algo):
        encobj = PRESENT()
    elif ("xTEA" == algo):
        encobj = xTEA(XTEA_KEY)
    elif ("AES128" == algo):
        encobj = AES(AES_KEY)
    else:
        pass
    return encobj

def initializeencryptionscheme(nonce_algo,
                               keystream_gen_algo,
                               mac_gen_algo,
                               canid):
    '''Function to initialize different encryption objects for encryption scheme'''
    global g_noncecreation, g_keystreamgen, g_macgeneration, g_canid
    global g_noncealgo, g_keystreamalgo, g_macgenalgo
    

    #Initilaize the objects for encryption scheme
    g_noncealgo = nonce_algo
    g_keystreamalgo = keystream_gen_algo
    g_macgenalgo = mac_gen_algo
    g_noncecreation = initencryptionobject(nonce_algo)
    g_keystreamgen = initencryptionobject(keystream_gen_algo)
    g_macgeneration = initencryptionobject(mac_gen_algo)
    g_canid = canid

def deinitencryptionscheme():
    '''Function to de-init different encryption objects for encryption scheme'''
    global g_noncecreation, g_keystreamgen, g_macgeneration, g_canid
    global g_noncealgo, g_keystreamalgo, g_macgenalgo

    #De-init the objects for encryption scheme
    g_noncecreation = None
    g_keystreamgen = None
    g_macgeneration = None
    g_canid = None

    g_noncealgo = None
    g_keystreamalgo = None
    g_macgenalgo = None


def setencryptionalgo(algorithm):
    '''Callback called on selecting the encyrption algorithm'''
    global g_encryptionalgo, g_encryption
    
    # Set the selected algorithm to the global variable
    g_encryptionalgo = algorithm

    #Initialize g_encryption object, based on the algorithm selected
    g_encryption = initencryptionobject(g_encryptionalgo)

    
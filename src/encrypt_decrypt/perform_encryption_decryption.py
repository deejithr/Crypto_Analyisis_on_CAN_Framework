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
from Crypto_Algorithms.AES_Cipher import *
from Crypto_Algorithms.SHA_Cipher import *
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
DECRYPT_OK = 1
DECRYPT_NOT_OK = 0

# Conversion Macros
CONVERT_S_TO_NS = 1_000_000_000
CONVERT_NS_TO_S = 1/ 1_000_000_000
CONVERT_NS_TO_MS = 1/ 1_000_000

#Encryption Algorithms
ENCRYPTION_ALGORITHMS = ["RC4", "SPECK", "xTEA", "PRESENT", "AES128"]
BENCHMARKPERIOD = [100, 50, 20, 10, 5]

# For Encryption State
DECRYTPION_WINDOW = 2

BENCHMARK_MESSAGE_COUNT=200
REPLAY_MESSAGE_COUNT = 500

################################################################################
# Globals
################################################################################
# Global Variable to store Encryption Algorithm
g_encryptionalgo = "RC4"

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

g_sendercounter = 0
g_receivercounter = 0

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

def generatemac(algo, encobj, data):
    if("AES128-CMAC" == algo):
        mac = encobj.generate_cmac_aes128(data, 2)
    elif("SHA256-HMAC" == algo):
        mac = encobj.generate_hmac_sha256(data, 2)
    return mac

def verifymac(algo, encobj, data, mac):
    if("AES128-CMAC" == algo):
        result = encobj.verify_cmac_aes128(data, 2, mac)
    elif("SHA256-HMAC" == algo):
        result = encobj.verify_hmac_sha256(data, 2, mac)
    return result

def encryption_scheme_encrypt(data, ready_event):
    global g_canid, g_keystreamgen, g_noncecreation, g_macgeneration
    global g_noncealgo, g_keystreamalgo, g_macgenalgo, g_sendercounter
    
    #Append the counter and CANID to create input for Nonce creation
    sender_nonceinput = g_canid.to_bytes(4,'big') + g_sendercounter.value.to_bytes(4,'big')
    #Encrypt this Nonce using Nonce-encrytpion Algorithm
    sender_Nonce = encrypt(g_noncealgo, g_noncecreation, sender_nonceinput)
    # Generate Keystream with this Nonce
    sender_S = encrypt(g_keystreamalgo, g_keystreamgen, sender_Nonce)
    #Encrypted Payload
    C = []
    for byte_a, byte_b in zip(data[0:6], sender_S):
        C.append(byte_a ^ byte_b)
    #Convert C to bytearray
    C = bytes(C)

    #Perform MAC generation
    sender_macinput = g_canid.to_bytes(4,'big') + g_sendercounter.value.to_bytes(4,'big') + C
    sender_mac = generatemac(g_macgenalgo, g_macgeneration, sender_macinput)

    can_payload = sender_mac + C

    #Increment the counter, only if the Receiver event is set, to sync between sender and receiver
    if(True == ready_event.is_set()): 
        g_sendercounter.value += 1
    return can_payload

def encryption_scheme_decrypt(data, canid):
    global g_receivercounter

    #Append the counter and CANID to create input for Nonce creation
    nonceinput = canid.to_bytes(4,'big') + g_receivercounter.value.to_bytes(4,'big')
    #Encrypt this Nonce using Nonce-encrytpion Algorithm
    Nonce = encrypt(g_noncealgo, g_noncecreation, nonceinput)
    # Generate Keystream with this Nonce
    S = encrypt(g_keystreamalgo, g_keystreamgen, Nonce)
    #Encrypted Payload
    P = []
    for byte_a, byte_b in zip(data[0:6], S):
        P.append(byte_a ^ byte_b)
    #Convert P to bytearray
    P = bytes(P)
    return P

def perform_encryption(data, encrypt_samples, encrypt_cpuper,
                       encscheme_state, canid, isextended, ready_event
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
        data = encryption_scheme_encrypt(data, ready_event)
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

def isMessageAccepted(encstate, data, canid):
    global g_macgeneration, g_macgenalgo, g_receivercounter

    verificationstatus = DECRYPT_NOT_OK
    if(True == encstate):
        countercandidate = g_receivercounter.value + 1
        while (countercandidate <= g_receivercounter.value + DECRYTPION_WINDOW):
            #Perform MAC verification
            receiver_macinput = canid.to_bytes(4,'big') + countercandidate.to_bytes(4,'big') + data[2:]
            verificationstatus = verifymac(g_macgenalgo, g_macgeneration, receiver_macinput, data[0:2])
            if(DECRYPT_OK == verificationstatus):
                g_receivercounter.value = countercandidate
                break
            countercandidate += 1
    else:
        verificationstatus = DECRYPT_OK

    return verificationstatus


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
    if(DECRYPT_OK == isMessageAccepted(encscheme_state.get(), data, canid)):
        accepted = DECRYPT_OK
        #Implementation pending for other algorithms
        # Call decrytion function depending on the algorithm
        # to decrypt the data
        # Check if Encryption Scheme enabled
        if(True == encscheme_state.get()):
            data = encryption_scheme_decrypt(data, canid)
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
    elif (
          ("AES128" == algo) or
          ("AES128-CMAC" == algo)
    ):
        encobj = AES_Cipher(AES_KEY)
    elif ("SHA256-HMAC" == algo):
        encobj = SHA_Cipher(AES_KEY)
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
    global g_sendercounter, g_receivercounter
    

    #Initilaize the objects for encryption scheme
    g_noncealgo = nonce_algo
    g_keystreamalgo = keystream_gen_algo
    g_macgenalgo = mac_gen_algo
    g_noncecreation = initencryptionobject(nonce_algo)
    g_keystreamgen = initencryptionobject(keystream_gen_algo)
    g_macgeneration = initencryptionobject(mac_gen_algo)
    g_canid = canid

    g_sendercounter = multiprocessing.Value('i', 1)
    g_receivercounter = multiprocessing.Value('i', 1)

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

def getsendercounter():
    global g_sendercounter
    return g_sendercounter.value

def getreceivercounter():
    global g_receivercounter
    return g_receivercounter.value
    
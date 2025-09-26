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
import numpy as np



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




################################################################################
# Globals
################################################################################
# Global Variable to store Encryption Algorithm
g_encryptionalgo = "None"

#Encryption Class Object
g_encryption = None

#Global variables for collecting the encrypt and decrypt time samples
encrypt_samples = {}
decrypt_samples = {}


################################################################################
# Functions
################################################################################
def perf_meas_init():
    '''Initializes the sample arrays for capturing the time samples'''
    global encrypt_samples, decrypt_samples
    #Initialize the samples array
    for algo in ["None", "RC4", "SPECK", "TEA", "PRESENT", "HMAC" ]:
        encrypt_samples[algo] = []
        decrypt_samples[algo] = []

def perform_encryption(data):
    ''' Perfrom encryption using the selected Algorithm'''
    global encrypt_samples
    # Start Measurement
    encryptiontime = 0
    encryptionstarttime = time.perf_counter_ns()
    
    #Implementation pending for other algorithms
    # Call encryption function depending on the algorithm
    # to get the encrypted data
    if("RC4" == g_encryptionalgo):
        data = g_encryption.rc4encrypt(data, len(data))
    elif("SPECK" == g_encryptionalgo):
        data = g_encryption.speckencrypt(data)
    else:
        pass
    
    # Stop Measurement
    encryptionendtime = time.perf_counter_ns()
    
    #Time taken for encryption
    encryptiontime = (encryptionendtime - encryptionstarttime) / us_DURATION
    encrypt_samples[g_encryptionalgo].append(encryptiontime)
    
    return data, encryptiontime

def isMessageAccepted(data):
    # Implmentation Pending
    return DECRYPT_OK


def perform_decryption(data):
    '''Perform Decryption using the selected Algorithm'''
    global decrypt_samples
    accepted = DECRYPT_NOT_OK
    
    # Start Measurement
    decryptiontime = 0
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
        else:
            pass
    # End Measurement
    decryptionendtime = time.perf_counter_ns()

    #Time taken for decryption
    decryptiontime = (decryptionendtime - decryptionstarttime) / us_DURATION
    decrypt_samples[g_encryptionalgo].append(decryptiontime)
    return data, decryptiontime, accepted

def setencryptionalgo(algorithm):
    '''Callback called on selecting the encyrption algorithm'''
    global g_encryptionalgo, g_encryption
    global encrypt_samples, decrypt_samples
    
    # Set the selected algorithm to the global variable
    g_encryptionalgo = algorithm

    if ("RC4" == g_encryptionalgo):
        g_encryption = RC4(RC4_KEY, RC4_S_ARRAY_SIZE)
    elif ("SPECK" == g_encryptionalgo):
        g_encryption = SPECK(SPECK_KEY)
    else:
        pass
    # Reset the encryption and decryption samples
    encrypt_samples[g_encryptionalgo] = []
    decrypt_samples[g_encryptionalgo] = []

def getperfmetrics(sampletype):
    '''Called after simulation stopped to get the Performance metrics for each algorithm'''
    global encrypt_samples, decrypt_samples
    perfmetrics = {}
    if ("encryption_samples" == sampletype):
        samplearray = encrypt_samples
    elif ("decryption_samples" == sampletype):
        samplearray = decrypt_samples
    
    for eachalgo, samples in samplearray.items():
        if(len(samples) > 0):
            samples = np.array(samples)
            mean_ns = statistics.fmean(samples)
            p95 = np.percentile(samples, 95)
            p99 = np.percentile(samples, 99)
            jitter_ns = statistics.pstdev(samples)
            cyclesperbyte = mean_ns * CPU_FREQ_MHZ / 1000

            # Add data to the Metrics dictionary
            perfmetrics[eachalgo] = {
                "mean_ns" : '%.3f'%(mean_ns),
                "p95" : '%.3f'%(p95),
                "p99" : '%.3f'%(p99),
                "jitter_ns" : '%.3f'%(jitter_ns),
                "cycles/byte" : '%.3f'%(cyclesperbyte),
            }
    return perfmetrics
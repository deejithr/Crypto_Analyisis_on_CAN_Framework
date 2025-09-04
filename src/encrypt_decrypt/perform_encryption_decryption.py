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
from Crypto_Algorithms.RC4 import *



################################################################################
# Macros
################################################################################
RC4_KEY = b"2023ht65544"
RC4_S_ARRAY_SIZE = 256



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
    #Initialize the samples array
    for algo in ["None", "RC4", "Speck", "TEA", "CMAC", "HMAC" ]:
        encrypt_samples[algo] = []
        decrypt_samples[algo] = []

def perform_encryption(data):
    # Start Measurement
    encryptiontime = 0
    encryptionstarttime = time.perf_counter_ns()
    
    #Implementation pending for other algorithms
    # Call encryption function depending on the algorithm
    # to get the encrypted data
    if("RC4" == g_encryptionalgo):
        data = g_encryption.rc4encrypt(data, len(data))
    else:
        pass
    
    # Stop Measurement
    encryptionendtime = time.perf_counter_ns()
    
    #Time taken for encryption
    encryptiontime = (encryptionendtime - encryptionstarttime) / us_DURATION
    encrypt_samples[g_encryptionalgo].append(encryptiontime)
    
    return data, encryptiontime

def perform_decryption(data):
    # Start Measurement
    decryptiontime = 0
    decryptionstarttime = time.perf_counter_ns()

    #Implementation pending for other algorithms
    # Call decrytion function depending on the algorithm
    # to decrypt the data
    if("RC4" == g_encryptionalgo):
        data = g_encryption.rc4decrypt(data, len(data))
    else:
        pass
    # End Measurement
    decryptionendtime = time.perf_counter_ns()

    #Time taken for decryption
    decryptiontime = (decryptionendtime - decryptionstarttime) / us_DURATION
    decrypt_samples[g_encryptionalgo].append(decryptiontime)
    return data, decryptiontime

def setencryptionalgo(algorithm):
    global g_encryptionalgo, g_encryption
    
    # Set the selected algorithm to the global variable
    g_encryptionalgo = algorithm

    if ("RC4" == g_encryptionalgo):
        g_encryption = RC4(RC4_KEY, RC4_S_ARRAY_SIZE)
    else:
        pass
    # Reset the encryption and decryption samples
    encrypt_samples[g_encryptionalgo] = []
    decrypt_samples[g_encryptionalgo] = []

def getperfmetrics(sampletype):
    perfmetrics = {}
    if ("encryption_samples" == sampletype):
        samplearray = encrypt_samples
    elif ("decryption_samples" == sampletype):
        samplearray = decrypt_samples
    
    for eachalgo, samples in samplearray.items():
        samples.sort()
        mean_ns = statistics.fmean(samples)
        p95 = samples[int(0.95*len(samples))]
        p99 = samples[int(0.99*len(samples))]
        jitter_ns = statistics.pstdev(samples)

        # Add data to the Metrics dictionary
        perfmetrics[eachalgo] = {
            "mean_ns" : mean_ns,
            "p95" : p95,
            "p99" : p99,
            "jitter_ns" : jitter_ns,
        }
    return perfmetrics
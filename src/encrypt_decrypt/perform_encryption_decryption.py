"""
This module provides utility functions for Encryption and Decryption.

It includes :
    * Function to encrypt/decrypt

"""
################################################################################
# Imports
################################################################################
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



################################################################################
# Functions
################################################################################
def perform_encryption(data):
    #Implementation pending
    # Call encryption function depending on the algorithm
    # to get the encrypted data
    if("RC4" == g_encryptionalgo):
        data = g_encryption.rc4encrypt(data, len(data))
    else:
        pass

    return data

def perform_decryption(data):
    #Implementation pending
    # Call decrytion function depending on the algorithm
    # to decrypt the data
    if("RC4" == g_encryptionalgo):
        data = g_encryption.rc4decrypt(data, len(data))
    else:
        pass
    return data

def setencryptionalgo(algorithm):
    global g_encryptionalgo, g_encryption
    
    # Set to the global variable
    g_encryptionalgo = algorithm

    if ("RC4" == g_encryptionalgo):
        g_encryption = RC4(RC4_KEY, RC4_S_ARRAY_SIZE)
    else:
        pass
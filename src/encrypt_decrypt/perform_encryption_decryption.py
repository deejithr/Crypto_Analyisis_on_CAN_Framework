"""
This module provides utility functions for encryption and decryption based on 
the algorithm selected.

It includes :
    * Function to perform encryption/decryption of data

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
    #Implementation pending for other algorithms
    # Call encryption function depending on the algorithm
    # to get the encrypted data
    if("RC4" == g_encryptionalgo):
        data = g_encryption.rc4encrypt(data, len(data))
    else:
        pass

    return data

def perform_decryption(data):
    #Implementation pending for other algorithms
    # Call decrytion function depending on the algorithm
    # to decrypt the data
    if("RC4" == g_encryptionalgo):
        data = g_encryption.rc4decrypt(data, len(data))
    else:
        pass
    return data

def setencryptionalgo(algorithm):
    global g_encryptionalgo, g_encryption
    
    # Set the selected algorithm to the global variable
    g_encryptionalgo = algorithm

    if ("RC4" == g_encryptionalgo):
        g_encryption = RC4(RC4_KEY, RC4_S_ARRAY_SIZE)
    else:
        pass
"""
This module provides utility functions for SPECK encryption algorithm.

It includes :
    * Functions for encrypting and decrypting data using SPECK block cipher

"""
################################################################################
# Imports
################################################################################
import struct


################################################################################
# Macros
################################################################################
SPECK_BLOCK_SIZE = 64
SPECK_KEY = b"2023ht6554400000" # 128 bit (16bytes) Key
SPECK_KEY_SIZE = 128

# No of rounds for SPECK 64/128 
SPECK_ROUNDS = 27
SPECK_MOD = 2**int(SPECK_BLOCK_SIZE/2)


################################################################################
# Classes
################################################################################
class SPECK:
    '''Represents the SPECK Block Cipher Algorithm class'''
    def __init__(self, key):
        self.key = key
        self.keyexpansion()

    def keyexpansion(self):
        '''For Key expansion to generate keys for the rounds'''
        # Split the key into four 32-bit words
        key_words = list(struct.unpack("<4I", self.key))  # unpacking the key into four 32bit words in
                                                        #little endian manner. < - Little Endian,
                                                        # 4- parts, I- 32bitIntegers
        #Initialize 
        round_keys = [0] * SPECK_ROUNDS
        l = [0] * 3
        round_keys[0] = key_words[0]
        k = round_keys[0]
        l = key_words[1:]
        

        # Generate subsequent round keys
        for i in range(SPECK_ROUNDS - 1):
            x, y = speckround_f(l[i % 3], k, i)
            l[i % 3] = x
            k = y
            round_keys[i + 1] = k

        self.roundkeys = round_keys  # round keys list

    def speckencrypt(self, plaintext):
        '''For encryption with SPECK'''
        # Convert Plaintext to bytearray
        plaintext = bytearray(plaintext)
        # Split 64-bit block into two 32-bit halves (x, y)
        x, y = struct.unpack("<2I", plaintext) # unpacking the plaintext into two 32bit words in
                                                #little endian manner. < - Little Endian,
                                                # 2- parts, I- 32bitIntegers

        for k in self.roundkeys:
            x, y = speckround_f(x, y, k)

        return struct.pack("<2I", x, y)
    
    def speckdecrypt(self, ciphertext):
        '''For SPECK decryption'''
        x, y = struct.unpack("<2I", ciphertext)

        for k in reversed(self.roundkeys):
            x, y = speckround_b(x, y, k)

        return struct.pack("<2I", x, y)


################################################################################
# Functions
################################################################################
# Rotation functions
def ROR(x, r):  # Rotate Right
    return ((x >> r) | (x << (int(SPECK_BLOCK_SIZE/2) - r))) & (SPECK_MOD - 1)

def ROL(x, r):  # Rotate Left
    return ((x << r) | (x >> (int(SPECK_BLOCK_SIZE/2) - r))) & (SPECK_MOD - 1)

def speckround_f(x, y, k):
    """The forward round function for SPECK."""
    x = ROR(x, 8)
    x = (x + y) & (SPECK_MOD - 1)
    x = x ^ k
    y = ROL(y, 3)
    y = y ^ x
    return x, y

def speckround_b(x, y, k):
    """The inverse round function for SPECK."""
    y = y ^ x
    y = ROR(y, 3)
    x = x ^ k
    x = (x - y) & (SPECK_MOD - 1)
    x = ROL(x, 8)
    return x, y


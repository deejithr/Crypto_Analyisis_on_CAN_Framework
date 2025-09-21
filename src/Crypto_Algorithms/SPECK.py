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
        k = [key_words[0]]
        l = key_words[1:]

        # Round Key Generation
        for i in range(SPECK_ROUNDS - 1):
            l_i = (ROR(l[i], 8) + k[i]) & 0xFFFFFFFF
            l_i ^= i
            k_i = ROL(k[i], 3) ^ l_i

            l.append(l_i)
            k.append(k_i)

        self.roundkeys = k  # round keys list

    def speckencrypt(self, plaintext):
        '''For encryption with SPECK'''
        # Convert Plaintext to bytearray
        plaintext = bytearray(plaintext)
        # Split 64-bit block into two 32-bit halves (x, y)
        x, y = struct.unpack("<2I", plaintext) # unpacking the plaintext into two 32bit words in
                                                #little endian manner. < - Little Endian,
                                                # 2- parts, I- 32bitIntegers

        for k in self.roundkeys:
            x = (ROR(x, 8) + y) & 0xFFFFFFFF
            x ^= k
            y = ROL(y, 3) ^ x

        return struct.pack("<2I", x, y)
    
    def speckdecrypt(self, ciphertext):
        '''For SPECK decryption'''
        x, y = struct.unpack("<2I", ciphertext)

        for k in reversed(self.roundkeys):
            y = ROR(y ^ x, 3)
            x = (ROL((x ^ k), 8) - y) & 0xFFFFFFFF

        return struct.pack("<2I", x, y)


################################################################################
# Functions
################################################################################
# Rotation functions
def ROR(x, r):  # Rotate Right
    return ((x >> r) | (x << (int(SPECK_BLOCK_SIZE/2) - r))) & 0xFFFFFFFF

def ROL(x, r):  # Rotate Left
    return ((x << r) | (x >> (int(SPECK_BLOCK_SIZE/2) - r))) & 0xFFFFFFFF

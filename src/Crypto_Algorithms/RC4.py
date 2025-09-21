"""
This module provides utility functions for RC4 encryption algorithm.

It includes :
    * Functions for encrypting and decrypting data using RC4 cipher

"""
################################################################################
# Imports
################################################################################




################################################################################
# Macros
################################################################################
# Key and array size information for RC4 Algorithm
RC4_KEY = b"2023ht65544"
RC4_S_ARRAY_SIZE = 256


# To represent time in 1 us
us_DURATION = 1_000



################################################################################
# Classes
################################################################################
class RC4:
    '''Represents the RC4 Algorithm class'''
    def __init__(self, key, s_arraysize):
        self.s_arraysize = s_arraysize
        self.key = key

    def keyschedulealgo(self):
        '''For Keyscheduling'''
        # Create S array, from 0 to s_arraysize
        self.s_array = list(range(self.s_arraysize))
        self.j = 0
        # keyshedalgo:  self.i from 0 to s_arraysize - 1
        for self.i in range(self.s_arraysize):
            # keyshedalgo: self.j = self.j + s[self.i] + key[self.i] mod s_arraysize
            self.j = (self.j + self.s_array[self.i] + self.key[self.i % len(self.key)]) % self.s_arraysize
            # keyshedalgo: swap s[self.i] and s[self.j]
            self.s_array[self.i], self.s_array[self.j] = self.s_array[self.j], self.s_array[self.i]

    def pseudorandomgen(self, datalen):
        '''For Pseudo Random Generator'''
        # Set i and j back to 0
        self.i = 0
        self.j = 0
        keystream = []
        for self.i in range(self.i + 1, datalen+1):
            self.j = (self.j + self.s_array[self.i]) % self.s_arraysize
            # swap s_array[i] and s_array[j]
            self.s_array[self.i], self.s_array[self.j] = self.s_array[self.j], self.s_array[self.i]
            #Temp byte
            t_byte = self.s_array[(self.s_array[self.i] + self.s_array[self.j]) % self.s_arraysize]
            # Append to the keystream
            keystream.append(t_byte)
        return keystream

    def rc4encrypt(self, plaintext, datalen):
        '''For RC4 encryption'''
        ciphertext = []
        # call Key Scheduling algorithm
        self.keyschedulealgo()
        # generate Keystream 
        keystream = self.pseudorandomgen(datalen)
        # perform encryption
        for iter in range(datalen):
            ciphertext.append(plaintext[iter] ^ keystream[iter])
        # return encrypted data
        return ciphertext
    
    def rc4decrypt(self, ciphertext, datalen):
        '''For RC4 decryption'''
        return self.rc4encrypt(ciphertext,datalen)


################################################################################
# Functions
################################################################################


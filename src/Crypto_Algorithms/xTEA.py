"""
This module provides utility functions for xTEA encryption algorithm.

It includes :
    * Functions for encrypting and decrypting data using xTEA (Extended TEA) cipher

"""
################################################################################
# Imports
################################################################################
import struct

################################################################################
# Macros
################################################################################
# 128 bit (16bytes) Key
XTEA_KEY = b"2023ht6554400000"
XTEA_NUM_ROUNDS=32

# The 32-bit Modulo (2^32)
MOD = 0xFFFFFFFF + 1 

# Delta constant for XTEA
DELTA = 0x9E3779B9 

################################################################################
# Classes
################################################################################
class xTEA:
    '''Represents the xTEA Cipher Algorithm class'''
    def __init__(self, key):
        self.key = key

    def convert_to_u32(self,val):
        """Ensures a value is represented as a positive 32-bit unsigned integer."""
        # This handles Python's potentially negative results from the % MOD operation
        return val % MOD

    def encrypt_xtea(self, data):
        """Encrypts a 64-bit data block using the XTEA algorithm."""
        data = bytearray(data)
        v0, v1 = struct.unpack('>LL', data)
        k = struct.unpack('>LLLL', self.key)

        sum_val = 0

        # Encryption Rounds
        for i in range(XTEA_NUM_ROUNDS):
            # 1. Update Sum: sum_val += DELTA (mod 2^32)
            sum_val = self.convert_to_u32(sum_val + DELTA)

            # 2. Modify v0:
            # F_key_select = k[sum_val & 3]
            # F_inner = ((v1 << 4) ^ (v1 >> 5)) + v1 (all mod 2^32)
            # F_term = F_inner ^ (sum_val + F_key_select) (mod 2^32)

            # Note: (v1 << 4) ^ (v1 >> 5) is naturally 32-bit if v1 is
            # We ensure it wraps using self.convert_to_u32
            F_inner = self.convert_to_u32((v1 << 4) ^ (v1 >> 5) + v1)
            F_term = self.convert_to_u32(F_inner ^ (sum_val + k[sum_val & 3]))

            v0 = self.convert_to_u32(v0 + F_term)

            # 3. Modify v1:
            # G_key_select = k[(sum_val >> 11) & 3]
            # G_inner = ((v0 << 4) ^ (v0 >> 5)) + v0 (all mod 2^32)
            # G_term = G_inner ^ (sum_val + G_key_select) (mod 2^32)

            G_inner = self.convert_to_u32((v0 << 4) ^ (v0 >> 5) + v0)
            G_term = self.convert_to_u32(G_inner ^ (sum_val + k[(sum_val >> 11) & 3]))

            v1 = self.convert_to_u32(v1 + G_term)

        return struct.pack('>LL', v0, v1)

    def decrypt_xtea(self, data):
        """Decrypts a 64-bit data block using the XTEA algorithm."""
        v0, v1 = struct.unpack('>LL', data)
        k = struct.unpack('>LLLL', self.key)

        # Initial Sum: sum_val starts at DELTA * XTEA_NUM_ROUNDS (mod 2^32)
        sum_val = self.convert_to_u32(DELTA * XTEA_NUM_ROUNDS)

        # Decryption Rounds (reverse order)
        for i in range(XTEA_NUM_ROUNDS):
            # 1. Reverse Modify v1 (using subtraction):
            # We must use the 'sum_val' *before* decrementing it.
            G_inner = self.convert_to_u32((v0 << 4) ^ (v0 >> 5) + v0)
            G_term = self.convert_to_u32(G_inner ^ (sum_val + k[(sum_val >> 11) & 3]))

            # The subtraction must correctly wrap around to 2^32-1, if the result is negatived
            v1 = self.convert_to_u32(v1 - G_term)

            # 2. Reverse Modify v0 (using subtraction):
            F_inner = self.convert_to_u32((v1 << 4) ^ (v1 >> 5) + v1)
            F_term = self.convert_to_u32(F_inner ^ (sum_val + k[sum_val & 3]))

            v0 = self.convert_to_u32(v0 - F_term)

            # 3. Reverse Update Sum: sum_val -= DELTA (mod 2^32)
            sum_val = self.convert_to_u32(sum_val - DELTA)

        return struct.pack('>LL', v0, v1)
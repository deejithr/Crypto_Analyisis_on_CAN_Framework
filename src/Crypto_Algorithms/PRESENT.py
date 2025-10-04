"""
This module provides utility functions for PRESENT encryption algorithm.

It includes :
    * Functions for encrypting and decrypting data using PRESENT

"""
################################################################################
# Imports
################################################################################




################################################################################
# Macros
################################################################################
# Key and rounds for PRESENT Algorithm
PRESENT_KEY = b"2023ht6554" 
PRESENT_ROUNDS = 31


################################################################################
# Globals
################################################################################
# S-box for PRESENT (Substitution box)
S_BOX = [
    0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2
]

# Inverse S-box for PRESENT (for decryption)
INV_S_BOX = [
    0x5, 0xE, 0xF, 0x8, 0xC, 0x1, 0x2, 0xD, 0xB, 0x4, 0x6, 0x3, 0x0, 0x7, 0x9, 0xA
]

# P-box for PRESENT (Permutation box)
P_BOX = [
    0, 16, 32, 48, 1, 17, 33, 49, 2, 18, 34, 50, 3, 19, 35, 51,
    4, 20, 36, 52, 5, 21, 37, 53, 6, 22, 38, 54, 7, 23, 39, 55,
    8, 24, 40, 56, 9, 25, 41, 57, 10, 26, 42, 58, 11, 27, 43, 59,
    12, 28, 44, 60, 13, 29, 45, 61, 14, 30, 46, 62, 15, 31, 47, 63
]
################################################################################
# Classes
################################################################################
class PRESENT:
    '''Represents the PRESENT Algorithm class'''
    def __init__(self):
        self.key = int(PRESENT_KEY.hex())
        self.rounds = PRESENT_ROUNDS
        self.round_keys = self.generate_round_keys()

    def generate_round_keys(self):
        '''Generate round keys for PRESENT Algorithm.
           Called during Initialization'''
        # Key schedule for PRESENT-80
        round_keys = []
        current_key = self.key
        for r in range(1, self.rounds + 1):
            round_keys.append(current_key >> 16) # K_i consists of the leftmost 64 bits of the current_key

            # Perform left rotation of 61 bits
            current_key = ((current_key & 0xFFFFFFFFFFFFFFFF) << 61) | (current_key >> 19)
            current_key &= 0xFFFFFFFFFFFFFFFFFFFF # Mask to keep it 80 bits

            # Perform S-box substitution on the 4 leftmost bits
            sbox_in = (current_key >> 76) & 0xF
            sbox_out = S_BOX[sbox_in]
            current_key = (current_key & 0x0FFFFFFFFFFFFFFFFFFF) | (sbox_out << 76)

            # Round counter addition
            current_key ^= (r << 15) & 0xFFFFFFFFFFFFFFFFFFFF # XOR with round counter
        return round_keys

    def add_round_key(self, state, round_key):
        '''Adding roundkey to plaintext in each round'''
        return state ^ round_key

    def s_box_layer(self, state, s_box_table):
        '''Perform Substitution'''
        new_state = 0
        for i in range(16): # 16 nibbles in a 64-bit state
            nibble = (state >> (i * 4)) & 0xF
            new_state |= (s_box_table[nibble] << (i * 4))
        return new_state

    def p_box_layer(self, state):
        '''Perform Permutation'''
        new_state = 0
        for i in range(64):
            if (state >> i) & 1:
                new_state |= (1 << P_BOX[i])
        return new_state

    def presentencrypt(self, plaintext):
        '''Perform Encryption'''
        plaintext = int("".join(f"{i:02x}" for i in plaintext), base=16)
        if len(bin(plaintext)[2:]) > 64:
            raise ValueError("Plaintext must be 64 bits or less.")

        state = plaintext
        for r in range(self.rounds - 1):
            state = self.add_round_key(state, self.round_keys[r])
            state = self.s_box_layer(state, S_BOX)
            state = self.p_box_layer(state)
        state = self.add_round_key(state, self.round_keys[self.rounds - 1]) # Last round without P-box and S-box

        #Convert to bytearray
        state_bytes = state.to_bytes(8, 'big')
        return bytearray(state_bytes)

    def presentdecrypt(self, ciphertext):
        '''Perform Decryption'''
        ciphertext = int("".join(f"{i:02x}" for i in ciphertext), base=16)
        if len(bin(ciphertext)[2:]) > 64:
            raise ValueError("Ciphertext must be 64 bits or less.")

        state = ciphertext
        state = self.add_round_key(state, self.round_keys[self.rounds - 1]) # First step of decryption

        for r in range(self.rounds - 2, -1, -1):
            state = self.p_box_layer_inverse(state)
            state = self.s_box_layer(state, INV_S_BOX)
            state = self.add_round_key(state, self.round_keys[r])

        #Convert to bytearray
        state_bytes = state.to_bytes(8, 'big')
        return bytearray(state_bytes)

    def p_box_layer_inverse(self, state):
        '''Perform Inverse Permutation for decryption'''
        # Inverse P-box is simply applying P_BOX in reverse
        new_state = 0
        for i in range(64):
            if (state >> P_BOX[i]) & 1:
                new_state |= (1 << i)
        return new_state        

    


################################################################################
# Functions
################################################################################
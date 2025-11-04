"""
This module provides utility functions for AES encryption algorithm.

It includes :
    * Functions for encrypting and decrypting data using AES (Advanced Encryption Cipher) cipher

"""
################################################################################
# Imports
################################################################################
import struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from Crypto.Cipher import AES
from Crypto.Hash import CMAC
from icecream import ic

################################################################################
# Macros
################################################################################
# 128 bit (16bytes) Key
AES_KEY = b"2023ht6554400000"
AES_KEY_SIZE = 16
AES_KEYSTREAM_SIZE = 8

################################################################################
# Globals
################################################################################


################################################################################
# Classes
################################################################################
class AES_Cipher:
    '''Represents the AES Algorithm class'''
    def __init__(self, key):
        self.key = key
        # Generate a strong, random 16-byte key (AES-128)
        # This key is the shared secret.
        self.nonce = os.urandom(AES_KEY_SIZE)
        

    def xor_bytes(self, a: bytes, b: bytes) -> bytes:
        """Performs a byte-by-byte XOR operation between two byte strings."""
        return bytes(x ^ y for x, y in zip(a, b))
    
    def aesencrypt(self, data):
        """ Performs encryption with AES in Counter Mode """
        ## 1. Initialize the AES-128 Cipher in CTR Mode
        # The key and the nonce/IV must be identical on both sender and receiver.
        cipher_send = Cipher(
            algorithms.AES(self.key), 
            modes.CTR(self.nonce), 
            backend=default_backend()
        )
        self.dummy_data = b'\x00' * AES_KEYSTREAM_SIZE
        self.sender_encryptor = cipher_send.encryptor()
        ## 2. Generate Keystream (8 bytes)
        # The `update()` method encrypts dummy data (zeros) to generate the keystream.
        self.keystream_sender =self.sender_encryptor.update(self.dummy_data)
        ## 3. XOR Keystream with CAN payload → Ciphertext
        ciphertext_payload = self.xor_bytes(data, self.keystream_sender)

        return ciphertext_payload
    
    def aesdecrypt(self, data):
        """ Performs decryption with AES in Counter Mode """
        ## 1. Initialize the AES-128 Cipher in CTR Mode
        # The key and the nonce/IV must be identical on both sender and receiver.
        cipher_recv = Cipher(
            algorithms.AES(self.key), 
            modes.CTR(self.nonce), 
            backend=default_backend()
        )
        self.dummy_data = b'\x00' * AES_KEYSTREAM_SIZE
        self.recv_decryptor = cipher_recv.encryptor()
        ## 2. Generate Keystream (8 bytes)
        # The `update()` method encrypts dummy data (zeros) to generate the keystream.
        self.keystream_recv =self.recv_decryptor.update(self.dummy_data)
        ## 3. XOR Keystream with Ciphertext → Plaintext
        plaintext_payload = self.xor_bytes(data, self.keystream_recv)

        return plaintext_payload
    
    def generate_cmac_aes128(self, message: bytes, tag_len: int = 4) -> bytes:
        '''Generate AES-128 CMAC tag for the given message.'''
        cmac = CMAC.new(self.key, ciphermod=AES)
        cmac.update(message)
        full_tag = cmac.digest()
        return full_tag[:tag_len]  # Truncate to fit 8B CAN frame
    
    def verify_cmac_aes128(self, message: bytes, taglen: bytes, mac) -> bool:
        '''Verify CMAC tag on receiver side.'''
        expected = self.generate_cmac_aes128(message, taglen)
        return expected == mac
        
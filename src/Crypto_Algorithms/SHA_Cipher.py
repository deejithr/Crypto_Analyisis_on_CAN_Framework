"""
This module provides utility functions for SHA256 MAC Generation.

It includes :
    * Functions for generating and verifying MAC using SHA algorithm

"""
################################################################################
# Imports
################################################################################
import hmac
import hashlib

################################################################################
# Macros
################################################################################
# 128 bit (16bytes) Key
SHA_KEY = b"2023ht6554400000"
SHA_KEY_SIZE = 16
SHA_KEYSTREAM_SIZE = 8

################################################################################
# Globals
################################################################################


################################################################################
# Classes
################################################################################
class SHA_Cipher:
    '''Represents the SHA256 Algorithm class'''
    def __init__(self, key):
        self.key = key
    
    def generate_hmac_sha256(self, message: bytes, tag_len: int = 4) -> bytes:
        '''Generate HMAC-SHA256 tag for given message.'''
        mac = hmac.new(self.key, message, hashlib.sha256).digest()
        return mac[:tag_len]

    def verify_hmac_sha256(self, message: bytes, tag: bytes) -> bool:
        ''' Verify HMAC tag.'''
        expected = self.generate_hmac_sha256(message, len(tag))
        return hmac.compare_digest(expected, tag)
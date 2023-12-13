import random
import math

class RSA:
    # To encrypt the given number
    def encrypt(self, message, public_key, n):
        e = public_key
        encrypted_text = 1
        while e > 0:
            encrypted_text *= message
            encrypted_text %= n
            e -= 1
        return encrypted_text


    # To decrypt the given number
    def decrypt(self, encrypted_text, private_key, n):
        d = private_key
        decrypted = 1
        while d > 0:
            decrypted *= encrypted_text
            decrypted %= n
            d -= 1
        return decrypted

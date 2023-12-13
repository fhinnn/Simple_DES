import socketio
import time
import random
import math


from des import DES
from utils import Utils
from rsa import RSA


des = DES()
rsa = RSA()
utils = Utils()


sio = socketio.Client()


def generateKey(key):
    key = key.upper()

    key = utils.hex2bin(key)

    keyp = [57, 49, 41, 33, 25, 17, 9,
            1, 58, 50, 42, 34, 26, 18,
            10, 2, 59, 51, 43, 35, 27,
            19, 11, 3, 60, 52, 44, 36,
            63, 55, 47, 39, 31, 23, 15,
            7, 62, 54, 46, 38, 30, 22,
            14, 6, 61, 53, 45, 37, 29,
            21, 13, 5, 28, 20, 12, 4]

    key = des.permute(key, keyp, 56)

    shift_table = [1, 1, 2, 2,
                2, 2, 2, 2,
                1, 2, 2, 2,
                2, 2, 2, 1]

    key_comp = [14, 17, 11, 24, 1, 5,
                3, 28, 15, 6, 21, 10,
                23, 19, 12, 4, 26, 8,
                16, 7, 27, 20, 13, 2,
                41, 52, 31, 37, 47, 55,
                30, 40, 51, 45, 33, 48,
                44, 49, 39, 56, 34, 53,
                46, 42, 50, 36, 29, 32]

    left = key[0:28]  # rkb for RoundKeys in binary
    right = key[28:56]  # rk for RoundKeys in hexadecimal

    rkb = []
    rk = []
    for i in range(0, 16):
        left = des.shift_left(left, shift_table[i])
        right = des.shift_left(right, shift_table[i])

        combine_str = left + right

        round_key = des.permute(combine_str, key_comp, 48)

        rkb.append(round_key)
        rk.append(utils.bin2hex(round_key))

    return rk, rkb

def encrypt_des(text, key):
    rk, rkb = generateKey(key)

    pt_all = utils.string_to_hexadecimal(text).upper()
    pt_chunks = [pt_all[i:i + 16] for i in range(0, len(pt_all), 16)]
    if len(pt_chunks[-1]) % 16 != 0:
        while len(pt_chunks[-1]) % 16 != 0:
            pt_chunks[-1] += "20"

    cipher_text_all = ""

    for i,pt in enumerate(pt_chunks):
        cipher_text_hexa = utils.bin2hex(des.encrypt(pt, rkb, rk))
        cipher_text = utils.hexadecimal_to_string(cipher_text_hexa)
        cipher_text_all += cipher_text

    return cipher_text_all

def decrypt_des(text, key):
    rk, rkb = generateKey(key)
    
    cipher_text_hexa_all = utils.string_to_hexadecimal(text).upper()
    cipher_text_hexa_all_chunks = [cipher_text_hexa_all[i:i + 16] for i in range(0, len(cipher_text_hexa_all), 16)]

    text_all = ""
    text_hexa_all = ""

    for i,cipher_text_hexa in enumerate(cipher_text_hexa_all_chunks):
        rkb_rev = rkb[::-1]
        rk_rev = rk[::-1]
        text_hexa = utils.bin2hex(des.encrypt(cipher_text_hexa, rkb_rev, rk_rev))
        text_hexa_all += text_hexa
        text = utils.hexadecimal_to_string(text_hexa)
        text_all += text

    text_hexa_all_chunks = [text_hexa_all[i:i + 16] for i in range(0, len(text_hexa_all), 16)]
    text_all = text_all.rstrip()

    return text_all

# A set will be the collection of prime numbers,
# where we can select random primes p and q
prime = set()

my_public_key = None
my_private_key = None
n = None

# We will run the function only once to fill the set of
# prime numbers
def primefiller():
    # Method used to fill the primes set is Sieve of
    # Eratosthenes (a method to collect prime numbers)
    seive = [True] * 250
    seive[0] = False
    seive[1] = False
    for i in range(2, 250):
        for j in range(i * 2, 250, i):
            seive[j] = False

    # Filling the prime numbers
    for i in range(len(seive)):
        if seive[i]:
            prime.add(i)


# Picking a random prime number and erasing that prime
# number from list because p!=q
def pickrandomprime():
    global prime
    k = random.randint(0, len(prime) - 1)
    it = iter(prime)
    for _ in range(k):
        next(it)

    ret = next(it)
    prime.remove(ret)
    return ret


def setkeys():
    global my_public_key, my_private_key, n
    prime1 = pickrandomprime() # First prime number
    prime2 = pickrandomprime() # Second prime number

    n = prime1 * prime2
    fi = (prime1 - 1) * (prime2 - 1)

    e = 2
    while True:
        if math.gcd(e, fi) == 1:
            break
        e += 1

    # d = (k*Φ(n) + 1) / e for some integer k
    my_public_key = f"{n}:{e}"

    d = 2
    while True:
        if (d * e) % fi == 1:
            break
        d += 1

    my_private_key = d


# First converting each character to its ASCII value and
# then encoding it then decoding the number to get the
# ASCII and converting it to character
def encrypt_rsa(message, public_key):
    n = int(public_key.split(':')[0])
    e = int(public_key.split(':')[1])
    encoded = []
    # Calling the encrypting function in encoding function
    for letter in message:
        encoded.append(rsa.encrypt(ord(letter.upper()), e, n))
    return encoded


def decrypt_rsa(encoded):
    global my_private_key, n
    s = ''
    # Calling the decrypting function decoding function
    for num in encoded:
        s += chr(rsa.decrypt(num, my_private_key, n))
    return s


username = input("Enter your username: ")

connected_users = []
received_messages = []

@sio.event
def connect():
    global connected_users
    print("Connected to server")
    sio.emit('set_username', {'username': username, 'public_key': my_public_key})

@sio.event
def disconnect():
    print("Disconnected from server")

@sio.event
def receive_message(data):
    sender_sid = data['sender_sid']
    encrypted_text = data['encrypted_text']
    encrypted_encryption_key = data['encrypted_encryption_key']
    global received_messages
    received_messages.append({'sender_sid': sender_sid, 'text': encrypted_text, 'encrypted_encryption_key': encrypted_encryption_key})

@sio.event
def open_message(data):
    print(f"Received Message from {data['username']}: {data['text']}")

@sio.event
def user_list(data):
    global connected_users
    for user in data['users']:
        if user not in connected_users:
            connected_users.append(user)

if __name__ == '__main__':
    primefiller()
    setkeys()
    server_url = 'http://localhost:6969'
    sio.connect(server_url)
    sio.emit('get_user_list')
    
    while True:
        sio.emit('get_user_list')
        print("\nMenu:")
        print("1. Send Message")
        print("2. Receive Message")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            while True:
                sio.emit('get_user_list')
                time.sleep(1)
                print("Choose a user to send a message:")
                for i, user in enumerate(connected_users, start=1):
                    print(f"{i}. {user['username']}")
                
                try:
                    choice = int(input("Enter the number of the user: "))
                    recipient_sid = connected_users[choice - 1]['sid']
                    print("Recepient Username: ", connected_users[choice - 1]['username'])
                except (ValueError, IndexError):
                    print("Invalid choice. Please enter a valid number.")
                    continue
                
                encryption_key = input("Enter the key to encrypt the message: ")
                text_to_send = input("Enter message to send: ")
    
                encrypted_text = encrypt_des(text_to_send, encryption_key)

                # encrypt encryption_key with public key rsa from selected user
                encrypted_encryption_key = encrypt_rsa(encryption_key, connected_users[choice - 1]['public_key']) 
                
                sio.emit('send_message', {'text': encrypted_text, 'recipient_sid': recipient_sid, 'encrypted_encryption_key': encrypted_encryption_key})
                
                print("Send Again? (y/n)")
                exit_choice = input()
                if exit_choice == 'n':
                    break

        elif choice == '2':
            while True:
                sio.emit('get_user_list')
                time.sleep(1)
                print("Choose a user to open messages:")
                for i, user in enumerate(connected_users, start=1):
                    print(f"{i}. {user['username']}")
                
                try:
                    choice = int(input("Enter the number of the user: "))
                    sender_user = connected_users[choice - 1]
                except (ValueError, IndexError):
                    print("Invalid choice. Please enter a valid number.")
                    continue
                

                print(f"Total Messages Received: {len(received_messages)}")
                
                if len(received_messages) != 0:

                    print(f"Messages from {sender_user['username']}:")
                    for message in received_messages:
                        if message['sender_sid'] == sender_user['sid']:
                            encrypted_decryption_key = message['encrypted_encryption_key']
                            decryption_key = decrypt_rsa(encrypted_decryption_key)
                            decrypted_text = decrypt_des(message['text'], decryption_key)       
                            print(f"Received Message from {sender_user['username']}: {decrypted_text}")
                
                time.sleep(1)
                print("Open Again? (y/n)")
                exit_choice = input()
                if exit_choice == 'n':
                    break
        elif choice == '3':
            break
                
    sio.disconnect()

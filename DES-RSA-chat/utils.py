class Utils:
    def __init__(self):
        pass
    def hex2bin(self,s):
        mp = {'0': "0000", '1': "0001", '2': "0010", '3': "0011", '4': "0100", '5': "0101",
            '6': "0110", '7': "0111", '8': "1000", '9': "1001", 'A': "1010", 'B': "1011",
            'C': "1100", 'D': "1101", 'E': "1110", 'F': "1111"}
        bin_str = ""
        for i in range(len(s)):
            bin_str = bin_str + mp[s[i]]
        return bin_str

    def bin2hex(self,s):
        mp = {"0000": '0', "0001": '1', "0010": '2', "0011": '3', "0100": '4', "0101": '5',
            "0110": '6', "0111": '7', "1000": '8', "1001": '9', "1010": 'A', "1011": 'B',
            "1100": 'C', "1101": 'D', "1110": 'E', "1111": 'F'}
        hex_str = ""
        for i in range(0, len(s), 4):
            ch = ""
            ch = ch + s[i]
            ch = ch + s[i + 1]
            ch = ch + s[i + 2]
            ch = ch + s[i + 3]
            hex_str = hex_str + mp[ch]
        return hex_str

    def bin2dec(self,binary):
        binary1 = binary
        decimal, i, n = 0, 0, 0
        while(binary != 0):
            dec = binary % 10
            decimal = decimal + dec * pow(2, i)
            binary = binary//10
            i += 1
        return decimal

    def dec2bin(self,num):
        res = bin(num).replace("0b", "")
        if(len(res) % 4 != 0):
            div = len(res) / 4
            div = int(div)
            counter = (4 * (div + 1)) - len(res)
            for i in range(0, counter):
                res = '0' + res
        return res

    def is_hexadecimal(self,s):
        valid_characters = "0123456789ABCDEFabcdef"

        for char in s:
            if char not in valid_characters:
                return False

        return True

    def string_to_hexadecimal(self,input_string):
        # bytes_data = input_string.encode('utf-8')

        # hexadecimal_data = ''.join([format(byte, '02x') for byte in bytes_data])

        hexadecimal_data = ''.join([format(ord(char), '02x') for char in input_string])

        return hexadecimal_data

    def hexadecimal_to_string(self,hex_string):

        # bytes_data = bytes.fromhex(hex_string.upper())

        # decoded_string = bytes_data.decode('utf-8')

        decoded_string = ''.join([chr(int(hex_string[i:i+2], 16)) for i in range(0, len(hex_string), 2)])

        return decoded_string
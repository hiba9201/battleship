import hashlib


class Utils:
    @staticmethod
    def number_to_letters(number):
        res = ''
        while number >= 26:
            res += chr(ord('A') + number % 26)
            number = number // 26 - 1
        else:
            res += chr(ord('A') + number)
        return res[::-1]

    @staticmethod
    def letters_to_number(letters):
        res = 0
        for i in range(len(letters)):
            res += (ord(letters[-i]) - ord('A') + 1) * (26 ** i)
        return res - 1

    @staticmethod
    def get_ship_borders(x, y):
        return {'ceil_y': y + 2,
                'floor_y': y - 1,
                'ceil_x': x + 2,
                'floor_x': x - 1}


class TwitterUtils():
    @staticmethod
    def code(message, key):
        result = []
        key_len = len(key)
        for i in range(len(message)):
            result.append(chr((ord(message[i]) + ord(key[i % key_len])) %
                              65536))
        return ''.join(result)

    @staticmethod
    def decode(message, key):
        result = []
        key_len = len(key)
        for i in range(len(message)):
            result.append(chr((ord(message[i]) - ord(key[i % key_len]) +
                               65536) % 65536))
        return ''.join(result)

    @staticmethod
    def md5_hex(string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    @staticmethod
    def decode_pair(pair, password):
        return (TwitterUtils.decode(pair[0], password),
                TwitterUtils.decode(pair[1], password))

    @staticmethod
    def check_pair(data_pair):
        actual_checksum = TwitterUtils.md5_hex(data_pair[0])
        expected_checksum = data_pair[1]
        return actual_checksum == expected_checksum

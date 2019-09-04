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
    def username_input(player_calling):
        username = ''
        while not username or ' ' in username:
            username = input(f'{player_calling} player, enter name: ')
        return username.lstrip()

    @staticmethod
    def get_ship_borders(x, y):
        return {'ceil_y': y + 2,
                'floor_y': y - 1,
                'ceil_x': x + 2,
                'floor_x': x - 1}

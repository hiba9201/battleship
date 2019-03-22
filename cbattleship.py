from game.environment import *
import re


class Game:
    # TODO mistakes check
    def __init__(self, m=10, n=10):
        self.env = Environment(m, n)

    def place_ship(self, ship_len, rotation, x, letter):
        y = ord(letter) - ord('A')
        cells_to_take = []
        if rotation == 'ver':
            for i in range(ship_len):
                cells_to_take.append((x, y + i))
        elif rotation == 'hor':
            for i in range(ship_len):
                cells_to_take.append((x + i, y))
        else:
            print('Unknown rotation!')
            return False
        self.env.user_field.place_ship_on_field(cells_to_take, self.env,
                                                'user')

    def show_field(self, player):
        field = self.env.bot_field
        if player == 'user':
            field = self.env.user_field
        for x in range(self.env.user_field.width + 1):
            print(x, end='  ')
        print()
        for y in range(field.height):
            print(chr(ord('A') + y), end='  ')
            for x in range(field.width):
                if field.field[x][
                        y].state == CellState.ship:
                    print('S', end='  ')
                elif field.field[x][y].state == CellState.fired:
                    print('F', end='  ')
                elif field.field[x][y].state == CellState.dead:
                    print('D', end='  ')
                elif field.field[x][y].state == CellState.missed:
                    print('M', end='  ')
                else:
                    print('X', end='  ')
            print()

    def fire(self, x, letter):
        y = ord(letter) - ord('A')
        if len(self.env.user_stack) != 0:
            print('You should place all your fleet before fire!')
        else:
            print(self.env.bot_field.fire_cell(x, y, self.env))


# TODO mistakes check
if __name__ == '__main__':
    game = Game(10, 10)
    command = ''
    print('New game started. Enter command:')
    while command != 'quit' and command != 'bye':
        command = input()
        if command == 'show user':
            game.show_field('user')
        elif command == 'show bot':
            game.show_field('bot')
        elif re.match(r'place \d [a-z]{3} \d{1,2} [A-Z]', command):
            split = command.split(' ')
            game.place_ship(int(split[1]), split[2], int(split[3]) - 1,
                            split[4])
        elif re.match(r'fire \d{1,2} [A-Z]', command):
            split = command.split(' ')
            game.fire(int(split[1]) - 1, split[2])
        elif command == 'start new':
            game = Game()
        elif command == 'help':
            print('help - show this list')
            print('about - info about the app')
            print('show [user | bot] - show chosen field')
            print('start new - start new game')
            print('place [ship_len] [ver | hor] [d l] - place ship on', end='')
            print(' "dl" cell vertically or horizontally')
            print('fire [d l] - shoot in dl cell')
            print('quit - close the app')
        elif command != 'quit' and command != 'bye':
            print("Command '{}' doesn't exist! Enter 'help' for help".format(
                command))

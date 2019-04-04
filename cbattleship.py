from game.environment import *
import re


class Game:
    def __init__(self, m=10, n=10):
        self.env = Environment(m, n)

    def place_ship(self, ship_len, rotation, x, letter):
        y = ord(letter) - ord('A')
        cells_to_take = []
        if rotation == 'v':
            for i in range(ship_len):
                cells_to_take.append((x, y + i))
        elif rotation == 'h':
            for i in range(ship_len):
                cells_to_take.append((x + i, y))
        else:
            print('Unknown rotation!')
            return False
        print(self.env.user_field.place_ship_on_field(cells_to_take, self.env,
                                                      'user'))

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
                if (field.field[x][y].state, player) == (
                        CellState.ship, 'user'):
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
        if not self.env.is_fleet_placed():
            print('You should place all your fleet before fire!')
            return True
        else:
            result = self.env.bot_field.fire_cell(x, y, self.env, 'user')
            print(result)
            if result == "user destroyed bot's ship!" or \
                    result == 'user hit bot\'s ship!':
                if self.env.is_player_defeated('bot'):
                    print('user won!')
                return True
            elif result == "user can't shoot there!":
                return True
            else:
                return False

    def bot_fire(self):
        self.env.random_fire()
        if self.env.is_player_defeated('user'):
            print('bot won!')


# TODO mistakes check
if __name__ == '__main__':
    game = Game()
    command = ''
    print('New game started. Enter command:')
    while command != 'quit' and command != 'bye':
        command = input()
        if command == 'show user':
            game.show_field('user')
        elif command == 'show bot':
            game.show_field('bot')
        elif re.match(r'place \d [v|h] \d{1,2} [A-Z]', command):
            split = command.split(' ')
            game.place_ship(int(split[1]), split[2], int(split[3]) - 1,
                            split[4])
        elif re.match(r'fire \d{1,2} [A-Z]', command):
            split = command.split(' ')
            if not game.fire(int(split[1]) - 1, split[2]):
                game.bot_fire()
        elif command == 'start new':
            game = Game()
        elif command == 'help':
            print('help - show this list')
            print('about - info about the app')
            print('show [user | bot] - show chosen field')
            print('start new - start new game')
            print('place [ship_len] [v | h] [d L] - place ship on', end='')
            print(' "dL" cell vertically or horizontally')
            print('fire [d L] - shoot in "dL" cell')
            print('quit - close the app')
        elif command != 'quit' and command != 'bye':
            print("Command '{}' doesn't exist! Enter 'help' for help".format(
                command))

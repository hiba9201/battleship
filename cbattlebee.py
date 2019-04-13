from game.environment import *
import re


class Game:
    def __init__(self, side=6):
        self.env = Environment(side)
        self.user_won = False
        self.bot_won = False

    def place_ship(self, ship_len, rotation, x, letter):
        y = ord(letter) - ord('A')
        cells_to_take = []
        if rotation == 'vl':
            for i in range(ship_len):
                cells_to_take.append((x, y + i))
        elif rotation == 'vr':
            for i in range(ship_len):
                cells_to_take.append((x + i, y + i))
        elif rotation == 'h':
            for i in range(ship_len):
                cells_to_take.append((x + i, y))
        else:
            print('unknown rotation!')
            return False
        print(self.env.user_field.place_ship_on_field(cells_to_take, self.env,
                                                      'user'))

    def show_field(self, player):
        field = self.env.bot_field
        if player == 'user':
            field = self.env.user_field
        side_count = 0
        count = 0
        spaces_count = field.side * 2 - side_count
        for y in range(field.side * 2 - 1):
            print(' ' * spaces_count, end='')
            for x in range(count, len(field.field[y])):
                if (field.field[y][x].state, player) == (
                        CellState.ship, 'user'):
                    print('S', end='   ')
                elif field.field[y][x].state == CellState.fired:
                    print('F', end='   ')
                elif field.field[y][x].state == CellState.dead:
                    print('D', end='   ')
                elif field.field[y][x].state == CellState.missed:
                    print('M', end='   ')
                elif field.field[y][x].state == CellState.not_field:
                    print(' ', end='   ')
                else:
                    print('X', end='   ')
            print()
            if y < field.side - 1:
                side_count += 1
                spaces_count -= 2
            else:
                count += 1
                spaces_count += 2

    def fire_with_fire_turn(self, x, letter):
        y = ord(letter) - ord('A')
        if not self.env.is_user_fleet_placed():
            print('you should place all your fleet before fire!')
            return True
        else:
            result = self.env.bot_field.fire_cell(x, y, self.env, 'user')
            print(result)
            if result == "user destroyed bot's ship!" or \
                    result == 'user hit bot\'s ship!':
                if self.env.is_player_defeated('bot'):
                    self.user_won = True
                    print('user won!')
                return True
            elif result == "user can't shoot there!":
                return True
            else:
                return False

    def bot_fire(self):
        self.env.bot_fire()
        if self.env.is_player_defeated('user'):
            self.bot_won = True
            print('bot won!')


if __name__ == '__main__':
    game = Game()
    command = ''
    print('New game started. Enter command:')
    while command != 'quit' and command != 'bye':
        if game.user_won or game.bot_won:
            while command != 'y' and command != 'n':
                command = input('do you want to start a new game?[y / n]: ')
                if command == 'y':
                    print('New game started. Enter command:')
                    game = Game()
            if command == 'n':
                break

        command = input()
        if command == 'show user':
            game.show_field('user')
        elif command == 'show bot':
            game.show_field('bot')
        elif re.match(r'place \d \w{1,2} \d{1,2} [A-Z]', command):
            split = command.split(' ')
            game.place_ship(int(split[1]), split[2], int(split[3]) - 1,
                            split[4])
        elif re.match(r'fire \d{1,2} [A-Z]', command):
            split = command.split(' ')
            if not game.fire_with_fire_turn(int(split[1]) - 1, split[2]):
                game.bot_fire()
        elif command == 'start new':
            print('New game started. Enter command:')
            game = Game()
        elif command == 'help':
            print('help - show this list')
            print('show [user | bot] - show chosen field')
            print('start new - start new game')
            print('place [ship_len] [vl | vr | h] [d L] - place ship on',
                  end='')
            print(' "d L" cell vertically left/right or horizontally')
            print('fire [d L] - shoot in "d L" cell')
            print('quit - close the app')
        elif command != 'quit' and command != 'bye':
            print(f"Command '{command}' doesn't exist! Enter 'help' for help")

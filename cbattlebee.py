import re

import game.environment as env


class Game:
    def __init__(self, side=6):
        self.env = env.Environment(side)
        self.user_won = False
        self.bot_won = False

    @staticmethod
    def letters_to_number(letters):
        res = 0
        for i in range(len(letters)):
            res += (ord(letters[i]) - ord('A')) * (26 ** i)
        return res

    def place_ship(self, ship_len, rotation, x, letters):
        y = self.letters_to_number(letters)
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
            return
        print(self.env.user_field.place_ship_on_field(cells_to_take, self.env,
                                                      env.Player.USER))

    def fire_with_fire_turn(self, x, letters):
        y = self.letters_to_number(letters)
        if not self.env.is_user_fleet_placed():
            print('you should place all your fleet before fire!')
            return True
        else:
            result = self.env.bot_field.fire_cell(x, y, self.env,
                                                  env.Player.USER)
            print(env.Player.USER, result)
            if result == env.FireResult.DESTROYED or \
                    result == env.FireResult.HIT:
                if self.env.is_player_defeated(env.Player.BOT):
                    self.user_won = True
                    print('user won!')
                return True
            elif result == env.FireResult.UNABLE:
                return True
            else:
                return False

    def bot_fire(self):
        self.env.bot.fire(self.env)
        if self.env.is_player_defeated(env.Player.USER):
            self.bot_won = True
            print('bot won!')


class CommandExecutor:
    def __init__(self):
        self.commands = {}
        self.add_command('quit', lambda g, p: quit())
        self.add_command('show', lambda g, p: self.show(g, p))
        self.add_command('place', lambda g, d: self.place(g, d))
        self.add_command('fire', lambda g, p: self.fire(g, p))
        self.add_command('new', lambda g, d: self.start_new(g, d))
        self.add_command('help', lambda g, d: self.help(g, d))
        self.add_command('auto', lambda g, d: self.auto(g, d))

    def execute_command(self, cmd):
        if cmd not in self.commands.keys():
            print(f"Command '{cmd}' doesn't exist! Enter 'help' for help")
            return None
        else:
            return self.commands[cmd]

    def add_command(self, cmnd, action):
        self.commands[cmnd] = action

    @staticmethod
    def auto(cur_game, cmd_data):
        if len(cmd_data) != 1:
            print('Wrong command arguments amount')
        else:
            cur_game.env.generate_user_field()
            print('Field was generated')
        return cur_game

    @staticmethod
    def show(cur_game, cmd_data):
        if len(cmd_data) != 2:
            print('Wrong command arguments amount')
        elif cmd_data[1] == 'user':
            print(cur_game.env.user_field)
        elif cmd_data[1] == 'bot':
            print(cur_game.env.bot_field)
        else:
            print('Wrong player')
        return cur_game

    @staticmethod
    def place(cur_game, cmd_data):
        if len(cmd_data) != 5:
            print('Wrong command arguments amount')
        elif not re.match(r'place \d \w{1,2} \d{1,2} [A-Z]', ' '.join(cmd_data)):
            print('Wrong placement data')
        else:
            cur_game.place_ship(int(cmd_data[1]), cmd_data[2], int(cmd_data[3]) - 1, cmd_data[4])
        return cur_game

    @staticmethod
    def fire(cur_game, pos):
        if len(pos) != 3:
            print('Wrong command arguments amount')
        elif not re.match(r'fire \d{1,2} [A-Z]', ' '.join(pos)):
            print('Wrong fire data')
        elif not cur_game.fire_with_fire_turn(int(pos[1]) - 1, pos[2]):
            game.bot_fire()
        return cur_game

    @staticmethod
    def start_new(g, d):
        if len(d) > 1:
            print('More command arguments than expected')
            return g
        print('New game started. Enter command:')
        return Game()

    @staticmethod
    def help(g, d):
        if len(d) > 1:
            print('More command arguments than expected')
        else:
            print('help - show this list')
            print('show [user | bot] - show chosen field')
            print('new - start new game')
            print('place [ship_len] [vl | vr | h] [d L] - place ship on',
                  end='')
            print(' "d L" cell vertically left/right or horizontally')
            print('fire [d L] - shoot in "d L" cell')
            print("auto - automatically generate user's field")
            print('quit - close the app')
        return g


if __name__ == '__main__':
    game = Game()
    cmd_e = CommandExecutor()
    command = ''
    print('New game started. Enter command:')

    while True:
        if game.user_won or game.bot_won:
            if game.user_won or game.bot_won:
                while command != 'y' and command != 'n':
                    command = input(
                        'do you want to start a new game?[y / n]: ')
                    if command == 'y':
                        print('New game started. Enter command:')
                        game = Game()
                if command == 'n':
                    break

        command = input()
        data = command.split(' ')
        action = cmd_e.execute_command(data[0])
        if action is not None:
            game = action(game, data)

#!/usr/bin/env python3
import functools
import re
import os
import sys

if sys.platform != 'win32':
    import readline

import game.environment as genv


class ExitGame(Exception):
    pass


class Game:
    def __init__(self, side=6, diff=0, ship_max=4, mode='bot'):
        self.env = genv.Environment(side, diff, ship_max)
        self.mode = mode
        self.user_won = False
        self.bot_won = False
        print('New game started. Enter command:')

    @staticmethod
    def letters_to_number(letters):
        res = 0
        for i in range(len(letters)):
            res += (ord(letters[-i]) - ord('A') + 1) * (26 ** i)
        return res - 1

    def place_ship(self, ship_len, rotation, x, letters):
        y = self.letters_to_number(letters)
        print(y)
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
        res = self.env.user_field.place_ship_on_field(cells_to_take, self.env,
                                                      genv.Player.USER)
        if res == genv.PlacementResult.SUCCESS:
            print(res)
        elif res == genv.PlacementResult.UNABLE:
            print(genv.Player.USER, res)
        elif res == genv.PlacementResult.LENGTH:
            print(genv.Player.USER, res, ship_len)

    def fire_with_fire_turn(self, x, letters):
        y = self.letters_to_number(letters)
        if not self.env.is_user_fleet_placed():
            print('you should place all your fleet before fire!')
            return True

        result = self.env.bot_field.fire_cell(x, y, self.env,
                                              genv.Player.USER)
        print(genv.Player.USER, result)
        if result == genv.FireResult.DESTROYED or \
                result == genv.FireResult.HIT:
            if self.env.is_player_defeated(genv.Player.BOT):
                self.user_won = True
                print('user won!')
            return True
        if result == genv.FireResult.UNABLE:
            return True
        return False

    def bot_fire(self):
        self.env.bot.fire(self.env)
        if self.env.is_player_defeated(genv.Player.USER):
            self.bot_won = True
            print('bot won!')


# TODO separate commands execution and creation in different classes
class CommandExecutor:
    def __init__(self):
        self.commands = {}

    def execute_command(self, cmd):
        if cmd not in self.commands.keys():
            print(f"Command '{cmd}' doesn't exist! Enter 'help' for help")
            return None
        else:
            return self.commands[cmd]

    def command_decorator(self, function):
        @functools.wraps(function)
        def command_func(*args):
            return function(*args)

        self.commands[function.__name__] = command_func


class BaseCommands:
    executor = CommandExecutor()

    @executor.command_decorator
    def clear(g, d):
        """
clear - clears screen"""
        if sys.platform == 'win32':
            os.system('cls')
        else:
            os.system('clear')
        return g

    @executor.command_decorator
    def exit(g, d):
        """
exit - close the app"""
        raise ExitGame

    @executor.command_decorator
    def auto(cur_game, cmd_data):
        """
auto - automatically generate user's field"""
        if len(cmd_data) != 1:
            print('Wrong command arguments amount')
        else:
            cur_game.env.generate_user_field()
            print('Field was generated\r')
        return cur_game

    # TODO print stat
    @executor.command_decorator
    def show(cur_game, cmd_data):
        """
show [user | bot] - show chosen field"""
        if len(cmd_data) != 2:
            print('Wrong command arguments amount')
        elif cmd_data[1] == 'user':
            print(cur_game.env.user_field)
        elif cmd_data[1] == 'bot':
            print(cur_game.env.bot_field)
        else:
            print('Wrong player')
        return cur_game

    @executor.command_decorator
    def place(cur_game, cmd_data):
        """
place [ship_len] [vl | vr | h] [d L] - place ship on
"d L" cell vertically left/right or horizontally"""
        if len(cmd_data) != 5:
            print('Wrong command arguments amount')
        elif not re.match(r'place \d \w{1,2} \d{1,2} [A-Za-z]',
                          ' '.join(cmd_data)):
            print('Wrong placement data')
        else:
            cur_game.place_ship(int(cmd_data[1]), cmd_data[2],
                                int(cmd_data[3]) - 1, cmd_data[4].upper())
        return cur_game

    @executor.command_decorator
    def fire(cur_game, pos):
        """
fire [d L] - shoot in "d L" cell"""
        if len(pos) != 3:
            print('Wrong command arguments amount')
        elif not re.match(r'fire \d{1,2} [A-Za-z]', ' '.join(pos)):
            print('Wrong fire data')
        elif not cur_game.fire_with_fire_turn(int(pos[1]) - 1, pos[2].upper()):
            game.bot_fire()
        return cur_game

    @executor.command_decorator
    def new(g, d):
        """
new <side> <difficulty> <ship_max> <mode> - start new game
All arguments are optional:
side - side length
difficulty - difficulty 0 or 1
ship_max - maximum ship length
mode - game mode: hot_seat or bot. Not implemented yet!"""
        if len(d) > 5:
            print('More command arguments than expected')
            return g
        try:
            side = int(d[1]) if len(d) > 1 else 6
        except ValueError:
            print('Wrong side!')
            return g
        try:
            diff = int(d[2]) if len(d) > 2 else 0
        except ValueError:
            print('Wrong difficulty!')
            return g
        try:
            ship_max = int(d[3]) if len(d) > 3 else 4
        except ValueError:
            print('Wrong ship length!')
            return g
        if len(d) > 4:
            if d[4] != 'hot_seat' or d[4] != 'bot':
                print('Wrong mode!')
                return g
        mode = d[4] if len(d) > 4 else 'bot'
        return Game(side, diff, ship_max, mode)

    @executor.command_decorator
    def help(g, d):
        """
help - show commands list"""
        if len(d) > 2:
            print('More command arguments than expected')
        elif len(d) == 1:
            for cmnd in BaseCommands.executor.commands.items():
                print(cmnd[1].__doc__)
        else:
            print(BaseCommands.executor.commands[d[1]].__doc__)
        return g


if __name__ == '__main__':

    game = Game()
    cmd_e = BaseCommands()
    command = ''

    while True:
        if game.mode == 'bot':
            if game.user_won or game.bot_won:
                if game.user_won or game.bot_won:
                    while command != 'y' and command != 'n':
                        command = input(
                            'do you want to start a new game?[y / n]: ')
                        if command == 'y':
                            game = Game()
                    if command == 'n':
                        raise ExitGame
            command = input().strip()
            data = command.split()
            if command == '':
                continue
            action = cmd_e.executor.execute_command(data[0])
            if action is not None:
                try:
                    game = action(game, data)
                except ExitGame:
                    break
        elif game.mode == 'hot_seat':
            raise NotImplemented

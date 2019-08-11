#!/usr/bin/env python3
import functools
import re
import os
import sys
import enum

if sys.platform != 'win32':
    import readline

import game.environment as genv


class GameMode(enum.Enum):
    HOT_SEAT = 'hs'
    BOT = 'bot'


class ExitGame(Exception):
    pass


class Game:
    def __init__(self, side=6, diff=0, ship_max=4, mode='bot'):
        self.env = genv.Environment(side, diff, ship_max)
        self.mode = GameMode(mode)
        self.finish = False

        if self.mode == GameMode.BOT:
            username = ''
            while not username:
                username = input('Player, enter name: ')
            self.env.add_player(genv.PlayerType.USER, username)
            self.env.players[username].active = True
            self.env.add_player(genv.PlayerType.BOT, 'bot')
            print('New game with bot started. Enter command:')
        elif self.mode == GameMode.HOT_SEAT:
            username = ''
            while not username:
                username = input('first player, enter name: ')
            self.env.add_player(genv.PlayerType.USER, username)
            self.env.players[username].active = True
            username = ''
            while not username:
                username = input('second player, enter name: ')
            self.env.add_player(genv.PlayerType.USER, username)
            print('New hot seat game started. Enter command:')

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
        _, player = self.env.get_active_player()
        res = player.field.place_ship_on_field(cells_to_take, player)
        if res == genv.PlacementResult.SUCCESS:
            print(res)
        elif res == genv.PlacementResult.UNABLE:
            print(genv.PlayerType.USER, res)
        elif res == genv.PlacementResult.LENGTH:
            print(genv.PlayerType.USER, res, ship_len)

    def fire_with_fire_turn(self, x, letters):
        y = self.letters_to_number(letters)
        name1, player1 = self.env.get_active_player()
        _, player2 = self.env.get_nonactive_player()
        if not player1.is_fleet_placed():
            print('you should place all your fleet before fire!')
            return True

        result = player2.field.fire_cell(x, y, self.env, player1)
        print(player1.type, result)
        if result == genv.FireResult.DESTROYED or \
                result == genv.FireResult.HIT:
            if player2.is_player_defeated():
                self.finish = True
                print(name1 + ' won!')
            return True
        if result == genv.FireResult.UNABLE:
            return True
        return False

    def bot_fire(self):
        bot = self.env.players['bot']
        _, user = self.env.get_nonactive_player()
        bot.bot.fire(self.env)
        self.switch_players()
        if user.is_player_defeated():
            self.finish = True
            print('bot won!')

    def switch_players(self):
        _, player1 = self.env.get_active_player()
        name, player2 = self.env.get_nonactive_player()
        player1.active = False
        player2.active = True
        if self.mode == GameMode.HOT_SEAT:
            input('press any key to clear screen...')
            if sys.platform == 'win32':
                os.system('cls')
            else:
                os.system('clear')
        print(name + "'s move")


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
            return function(
                *args)  # something about errors/exceptions/etc checks

        self.commands[function.__name__] = command_func


class BaseCommands:  # TODO добавить вывод статистики
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
            if cur_game.mode == GameMode.HOT_SEAT:
                print('player placed their fleet')
                cur_game.switch_players()
            print('Field was generated\r')
        return cur_game

    # TODO print stat
    @executor.command_decorator
    def show(cur_game, cmd_data):
        """
show [username | bot] - show chosen field"""
        if len(cmd_data) != 2:
            print('Wrong command arguments amount')
        elif cmd_data[1] in cur_game.env.players.keys():
            print(cur_game.env.players[cmd_data[1]].field)
        else:
            print('Wrong player')
        return cur_game

    @executor.command_decorator
    def place(cur_game, cmd_data):
        """
place [ship_len] [vl | vr | h] [d L] - place ship with *ship_len* length on
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
            cur_game.switch_players()
            if cur_game.mode == GameMode.BOT:
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
mode - game mode: hs or bot"""
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
            if d[4] != GameMode.HOT_SEAT.value and d[4] != GameMode.BOT.value:
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

    @executor.command_decorator
    def stat(g, d):
        """
stat - show current gam statistics
        """
        pass


if __name__ == '__main__':

    game = Game()
    cmd_e = BaseCommands()
    command = ''

    while True:
        if game.finish:
            while command != 'y' and command != 'n':
                command = input('do you want to start a new game?[y / n]: ')
                if command == 'y':
                    game = Game()
            if command == 'n':
                cmd_e.executor.execute_command('exit')
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

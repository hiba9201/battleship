import enum
import random
import time
import sys

import game.utils as utils

if sys.platform == 'win32':
    try:
        import colorama

        colorama.init()
    except ImportError:
        pass


class CellState(enum.Enum):
    NOT_FIELD = ' '
    EMPTY = 'X'
    FIRED = 'F'
    DEAD = 'D'
    SHIP = 'S'
    MISSED = 'M'


class Color(enum.Enum):
    RED = '\033[31m'
    DEFAULT = '\033[0m'
    BLUE = '\033[94m'
    AQUA = '\033[34m'
    PURPLE = '\033[95m'
    BLACK = '\033[30m'
    GREEN = '\033[32m'

    def __str__(self):
        return self.value


class PlacementResult(enum.Enum):
    SUCCESS = "Ship was placed successfully!"
    UNABLE = "can't place ship there!"
    LENGTH = "doesn't have a ship with length"

    def __str__(self):
        return self.value


class FireResult(enum.Enum):
    UNABLE = 0
    DESTROYED = 1
    HIT = 2
    MISSED = 3

    def __str__(self):
        res = self.name.lower()
        if self.name == 'UNABLE':
            res += ' to shoot there'
        else:
            res += ' ship'
        return res


class PlayerType(enum.Enum):
    USER = 0
    BOT = 1

    def __str__(self):
        return self.name.lower()


class Cell:
    def __init__(self, x, y, state=CellState.EMPTY):
        self.x = x
        self.y = y
        self.state = state
        self.color = Color.GREEN

    def __ne__(self, other):
        return (self.x, self.y) != (other.x, other.y)


class Player:
    def __init__(self, typ, env):
        self.type = typ
        self.active = False
        self.field = Honeycomb(env.side, self, env)
        self.shots_count = 0
        self.missed_count = 0
        self.hand = [env.ship_max - x for x in
                     range(env.ship_max) for _ in range(x + 1)]
        self.fleet = 0
        while sum(self.hand) / self.field.square > 0.3:
            self.user_hand = [env.ship_max - x for x in
                              range(env.ship_max) for _ in
                              range(x + 1)]
        if typ == PlayerType.BOT:
            self.AI = BotAI(env.diff)
            if self.AI.diff != env.diff:
                env.diff = self.AI.diff
            self.bot = self.AI.bot(self)
            self.bot.generator(env)

    def is_ship_in_hand(self, ship_len):
        for ship in self.hand:
            if ship == ship_len:
                return True
        return False

    def move_ship_to_fleet(self, ship_len):
        for i in range(len(self.hand)):
            if self.hand[i] == ship_len:
                self.fleet += self.hand.pop(i)
                return True
        return False

    def is_player_defeated(self):
        return self.fleet == 0 and not self.hand

    def is_fleet_placed(self):
        return len(self.hand) == 0

    def delete_cell_from_fleet(self):
        self.fleet -= 1


class Environment:

    def __init__(self, side, diff, ship_max):
        self.ship_max = ship_max
        self.diff = diff
        self.side = side
        self.players = {}
        self.ship_cells = [ship_max - x for x in
                           range(ship_max) for _ in range(x + 1)]

    def player_exists(self, name):
        if name in self.players:
            return True
        return False

    def add_player(self, typ, name):
        if name not in self.players.keys():
            self.players[name] = Player(typ, self)
        else:
            raise KeyError

    def reset_player_data(self, player):
        player.field = Honeycomb(self.side, player.type, self)
        player.hand = [self.ship_max - x for x in range(self.ship_max)
                       for _ in range(x + 1)]
        player.fleet = 0

    def generate_user_field(self):
        _, player = self.get_active_player()
        while not player.field.auto_generate():
            self.reset_player_data(player)

    def get_active_player(self):
        for n, p in self.players.items():
            if p.active:
                return n, p

    def get_nonactive_player(self):
        for n, p in self.players.items():
            if not p.active:
                return n, p

    @property  # TODO add test
    def ships_count(self):
        return (1 + self.ship_max) * self.ship_max // 2


class Honeycomb:
    def __init__(self, side, player, env):
        self.side = side
        self.field = []
        self.owner = player
        self.poses = []
        self.square = 0
        self.corner_ships_count = 0
        self.env = env
        self.corners = ((0, 0),
                        (0, side - 1),
                        (side - 1, 0),
                        (side * 2 - 1, side - 1),
                        (side - 1, side * 2 - 1),
                        (side * 2 - 1, side * 2 - 1))

        side_count = 0
        count = 0
        for y in range(side * 2 - 1):
            self.field.append([])
            for x in range(side + side_count):
                if y >= self.side - 1 and x < count:
                    self.field[y].append(Cell(x, y, CellState.NOT_FIELD))
                else:
                    self.poses.append((x, y))
                    self.field[y].append(Cell(x, y))
                    self.square += 1
            if y < self.side - 1:
                side_count += 1
            else:
                count += 1

    def __str__(self):
        side_count = 0
        count = 0
        spaces_count = self.side * 2 - side_count
        result = [' ' * (spaces_count + 1) + '     ']

        for x in range(self.side):
            result.append(Color.BLUE.value + str(x + 1) + Color.DEFAULT.value +
                          '   ')
        result.append('\n')

        for y in range(self.side * 2 - 1):
            letters = utils.Utils.number_to_letters(y)
            result.append(' ' * (spaces_count - len(letters) + 1))
            result.append(Color.PURPLE.value + letters + Color.DEFAULT.value +
                          '   ')
            for x in range(count, len(self.field[y])):
                if (self.field[y][x].state == CellState.SHIP and
                        not self.owner.active):
                    result.append(self.field[y][x].color.value +
                                  CellState.EMPTY.value + Color.DEFAULT.value)
                elif (self.field[y][x].color == Color.GREEN and
                      self.owner.active and self.owner.is_fleet_placed()):
                    result.append(self.field[y][x].state.value)
                else:
                    result.append(self.field[y][x].color.value +
                                  self.field[y][x].state.value +
                                  Color.DEFAULT.value)
                result.append('   ')

            if y < self.side - 1:
                result.append(Color.BLUE.value +
                              str(len(self.field[y]) - count + 1) +
                              Color.DEFAULT.value)
                side_count += 1
                spaces_count -= 2
            else:
                count += 1
                spaces_count += 2
            result.append('\n')

        return ''.join(result)

    def is_in_bound(self, x, y):
        if not 0 <= y < (self.side * 2 - 1):
            return False

        for cell in self.field[y]:
            if cell.state != CellState.NOT_FIELD:
                index = self.field[y].index(cell)
                break
        return index <= x < len(self.field[y])

    def fire_cell(self, x, y, player):
        if not self.is_in_bound(x, y):
            return FireResult.UNABLE
        if self.field[y][x].state == CellState.SHIP:
            self.field[y][x].state = CellState.FIRED
            player.shots_count += 1
            self.field[y][x].color = Color.RED
            self.owner.delete_cell_from_fleet()
            if self.is_ship_dead(x, y, x, y):
                self.change_color_death(x, y, x, y)
                return FireResult.DESTROYED
            else:
                self.change_color_hit(x, y, Color.GREEN)
                return FireResult.HIT
        elif self.field[y][x].state == CellState.EMPTY:
            self.field[y][x].state = CellState.MISSED
            self.field[y][x].color = Color.AQUA
            player.shots_count += 1
            player.missed_count += 1
            return FireResult.MISSED
        else:
            return FireResult.UNABLE

    def change_color_hit(self, x, y, color):
        ship_limits = utils.Utils.get_ship_borders(x, y)
        borders = ((ship_limits['floor_y'], ship_limits['ceil_x'] - 1),
                   (ship_limits['ceil_y'] - 1, ship_limits['floor_x']))

        for i in range(ship_limits['floor_y'], ship_limits['ceil_y']):
            for j in range(ship_limits['floor_x'], ship_limits['ceil_x']):
                if (i, j) in borders or not self.is_in_bound(j, i):
                    continue
                if (self.field[i][j].state != CellState.MISSED and
                        self.field[i][j].color != Color.RED):
                    self.field[i][j].color = color

    def change_color_death(self, x, y, prev_x, prev_y):
        ship_limits = utils.Utils.get_ship_borders(x, y)
        borders = ((ship_limits['floor_y'], ship_limits['ceil_x'] - 1),
                   (ship_limits['ceil_y'] - 1, ship_limits['floor_x']))

        for i in range(ship_limits['floor_y'], ship_limits['ceil_y']):
            for j in range(ship_limits['floor_x'], ship_limits['ceil_x']):
                if (i, j) in borders or not self.is_in_bound(j, i):
                    continue
                if self.field[i][j].state == CellState.DEAD:
                    if not (self.field[i][j] in (
                            self.field[y][x], self.field[prev_y][prev_x])):
                        self.change_color_death(j, i, x, y)
                elif (self.field[y][x].state == CellState.DEAD and
                      self.field[i][j].state != CellState.MISSED):
                    self.field[i][j].color = Color.RED
        return True

    def is_ship_dead(self, x, y, prev_x, prev_y):
        ship_limits = utils.Utils.get_ship_borders(x, y)
        borders = ((ship_limits['floor_y'], ship_limits['ceil_x']),
                   (ship_limits['ceil_y'], ship_limits['floor_x']))

        for i in range(ship_limits['floor_y'], ship_limits['ceil_y']):
            for j in range(ship_limits['floor_x'], ship_limits['ceil_x']):
                if (i, j) in borders or not self.is_in_bound(j, i):
                    continue
                if self.field[i][j].state == CellState.FIRED:
                    if (self.field[i][j] != self.field[y][x] and
                            self.field[i][j] != self.field[prev_y][prev_x]):
                        if self.is_ship_dead(j, i, x, y):
                            continue
                        else:
                            return False
                elif self.field[i][j].state == CellState.SHIP:
                    return False
        self.field[y][x].state = CellState.DEAD
        self.field[y][x].color = Color.RED
        return True

    def clear_colors(self):
        for row in self.field:
            for cell in row:
                cell.color = Color.DEFAULT

    def place_ship_on_field(self, cells_to_take):
        taken_cells = []
        ship_len = len(cells_to_take)
        if not self.owner.is_ship_in_hand(ship_len):
            return PlacementResult.LENGTH
        for (x, y) in cells_to_take:
            if (x, y) in self.corners:
                if self.corner_ships_count + 1 > 0.1 * self.env.ships_count:
                    return PlacementResult.UNABLE
                self.corner_ships_count += 1
            if not self.is_in_bound(x, y):
                return PlacementResult.UNABLE

            ceil_y = min(y + 2, self.side * 2 - 1)
            floor_y = max(y - 1, 0)
            ceil_x = min(x + 2, len(self.field[y]))
            floor_x = max(x - 1, 0)
            borders = ((ceil_x, floor_y), (floor_x, ceil_y))
            for i in range(floor_x, ceil_x):
                for j in range(floor_y, ceil_y):
                    if (i, j) in borders or not self.is_in_bound(i, j):
                        continue
                    if ((self.field[j][i].state != CellState.EMPTY) and
                            self.field[j][i] not in taken_cells):
                        return PlacementResult.UNABLE
            taken_cells.append(self.field[y][x])
        for cell in taken_cells:
            self.change_color_hit(cell.x, cell.y, Color.RED)
            cell.state = CellState.SHIP
        self.owner.move_ship_to_fleet(ship_len)
        for pos in cells_to_take:
            self.poses.remove(pos)
        if not self.owner.hand:
            self.clear_colors()
        return PlacementResult.SUCCESS

    def auto_generate(self):
        hand = self.owner.hand
        random.seed()
        start_time = time.process_time()
        while hand:
            ship_len = hand[0]
            res = ''
            while res != PlacementResult.SUCCESS:
                rotation = random.choice(('vl', 'vr', 'h'))
                (x, y) = random.choice(self.poses)
                if rotation == 'vl':
                    cells_to_take = [(x, y + i) for i in range(ship_len)]
                elif rotation == 'vr':
                    cells_to_take = [(x + i, y + i) for i in range(ship_len)]
                else:
                    cells_to_take = [(x + i, y) for i in range(ship_len)]
                res = self.place_ship_on_field(cells_to_take)

                check_time = time.process_time()
                if check_time - start_time > 0.5:
                    return False
        return True

    def partition_auto_generate(self):
        hand = self.owner.hand
        random.seed()
        start_time = time.process_time()
        y_border = hand[0]
        x_border = 0
        while hand:
            ship_len = hand[0]
            x_border += ship_len
            if x_border > len(self.field[y_border]):
                x_border = ship_len
                if y_border + ship_len < self.side * 2 - 1:
                    y_border += ship_len
                else:
                    y_border = self.side * 2 - 1
            res = ''
            while res != PlacementResult.SUCCESS:
                rotation = random.choice(('vl', 'vr', 'h'))
                y = random.randrange(min(y_border, self.side * 2 - 1))
                x = random.randrange(min(x_border, len(self.field[y])))
                if rotation == 'vl':
                    cells_to_take = [(x, y + i) for i in range(ship_len)]
                elif rotation == 'vr':
                    cells_to_take = [(x + i, y + i) for i in range(ship_len)]
                else:
                    cells_to_take = [(x + i, y) for i in range(ship_len)]
                res = self.place_ship_on_field(cells_to_take)

                check_time = time.process_time()
                if check_time - start_time > 0.1:
                    return False

            if len(hand) == 1:
                self.auto_generate()
                break

        return True


class BotAI:
    def __init__(self, difficulty):
        try:
            self.bot = BotAI.__subclasses__()[difficulty]
            self.diff = difficulty
        except IndexError:
            self.bot = BotAI.__subclasses__()[0]
            self.diff = 0


class SimpleBotAI(BotAI):
    def __init__(self, bot):
        self.field = bot.field
        self.bot = bot

    def generator(self, env):
        print('Bot field is being generated')
        while not self.field.auto_generate():
            env.reset_player_data(self.bot)
        print('Field was generated successfully')

    def fire(self, env):
        _, enemy = env.get_nonactive_player()

        y = random.randrange(self.bot.field.side * 2 - 1)
        x = random.randrange(len(enemy.field.field[y]))
        result = enemy.field.fire_cell(x, y, self.bot)
        return result


class HardBotAI(BotAI):
    def __init__(self, bot):
        self.field = bot.field
        self.bot = bot
        self.last_fire = (-1, -1)

    def generator(self, env):
        print('Bot field is being generated')
        while not self.field.partition_auto_generate(self.bot):
            env.reset_player_data(self.bot)
        print('Field was generated successfully')

    def fire(self, env):
        _, enemy = env.get_nonactive_player()
        if self.last_fire == (-1, -1):
            y = random.randrange(enemy.field.side * 2 - 1)
            x = random.randrange(len(enemy.field.field[y]))
            result = enemy.field.fire_cell(x, y, self.bot)
        else:
            (prev_y, prev_x) = self.last_fire
            ceil_y = prev_y + 2
            floor_y = prev_y - 1
            ceil_x = prev_x + 2
            floor_x = prev_x - 1
            while True:
                y = random.randrange(floor_y, ceil_y)
                x = random.randrange(floor_x, ceil_x)
                if ((y, x) != (floor_y, ceil_x - 1) or
                        (y, x) != (ceil_y - 1, floor_x) or
                        self.field.is_in_bound(y, x)):
                    break
            result = enemy.field.fire_cell(x, y, self.bot)
        if result == FireResult.DESTROYED:
            self.last_fire = (-1, -1)
        elif result == FireResult.HIT:
            self.last_fire = (y, x)
        return result

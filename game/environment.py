import enum
import random
import time
import sys

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
        self.field = Honeycomb(env.side, self)
        self.hand = [env.ship_max - x for x in
                     range(env.ship_max) for _ in range(x + 1)]
        self.fleet = 0
        while sum(self.hand) / self.field.square > 0.3:
            self.user_hand = [env.ship_max - x for x in
                              range(env.ship_max) for _ in
                              range(x + 1)]
        if typ == PlayerType.BOT:
            self.bot = BotAI(env.diff).bot(self)
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

    def add_player(self, typ, name):
        if name not in self.players.keys():
            self.players[name] = Player(typ, self)
        else:
            raise KeyError

    def reset_player_data(self, player):
        player.field = Honeycomb(self.side, player.type)
        player.hand = [self.ship_max - x for x in range(self.ship_max)
                       for _ in range(x + 1)]
        player.fleet = 0

    def generate_user_field(self):
        _, player = self.get_active_player()
        while not player.field.auto_generate(player.hand, player):
            self.reset_player_data(player)

    def get_active_player(self):
        for n, p in self.players.items():
            if p.active:
                return n, p

    def get_nonactive_player(self):
        for n, p in self.players.items():
            if not p.active:
                return n, p


class Honeycomb:
    def __init__(self, side, player):
        self.side = side
        self.field = []
        self.owner = player
        self.poses = []
        self.square = 0

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

    @staticmethod
    def number_to_letters(number):
        res = ''
        while number >= 26:
            res += chr(ord('A') + number % 26)
            number = number // 26 - 1
        else:
            res += chr(ord('A') + number)
        return res[::-1]

    def __str__(self):
        side_count = 0
        count = 0
        spaces_count = self.side * 2 - side_count
        res = ' ' * (spaces_count + 1) + '     '

        for x in range(self.side):
            res += Color.BLUE.value + str(x + 1) + Color.DEFAULT.value
            res += '   '
        res += '\n'

        for y in range(self.side * 2 - 1):
            letters = self.number_to_letters(y)
            res += ' ' * (spaces_count - len(letters) + 1)
            res += (Color.PURPLE.value + letters +
                    Color.DEFAULT.value + '   ')
            for x in range(count, len(self.field[y])):
                if (self.field[y][x].state == CellState.SHIP and
                        not self.owner.active):
                    res += (self.field[y][x].color.value +
                            CellState.EMPTY.value + Color.DEFAULT.value)
                else:
                    res += (self.field[y][x].color.value +
                            self.field[y][x].state.value +
                            Color.DEFAULT.value)
                res += '   '
            if y < self.side - 1:
                res += Color.BLUE.value + str(
                    len(self.field[y]) - count + 1) + Color.DEFAULT.value
                side_count += 1
                spaces_count -= 2
            else:
                count += 1
                spaces_count += 2
            res += '\n'

        return res

    def is_in_bound(self, x, y):
        if not 0 <= y < (self.side * 2 - 1):
            return False

        for cell in self.field[y]:
            if cell.state != CellState.NOT_FIELD:
                index = self.field[y].index(cell)
                break
        return index <= x < len(self.field[y])

    def fire_cell(self, x, y, env, player):
        if not self.is_in_bound(x, y):
            return FireResult.UNABLE
        _, enemy = env.get_nonactive_player()
        if self.field[y][x].state == CellState.SHIP:
            self.field[y][x].state = CellState.FIRED
            if player.active:
                self.field[y][x].color = Color.RED
            else:
                self.field[y][x].color = Color.GREEN
            enemy.delete_cell_from_fleet()
            if self.is_ship_dead(x, y, x, y):
                if player.active:
                    self.change_color_death(x, y, x, y)
                return FireResult.DESTROYED
            else:
                if player.active:
                    self.change_color_hit(x, y, Color.GREEN)
                return FireResult.HIT
        elif self.field[y][x].state == CellState.EMPTY:
            self.field[y][x].state = CellState.MISSED
            self.field[y][x].color = Color.AQUA
            return FireResult.MISSED
        else:
            return FireResult.UNABLE

    def change_color_hit(self, x, y, color):
        ceil_y = y + 2
        floor_y = y - 1
        ceil_x = x + 2
        floor_x = x - 1
        for i in range(floor_y, ceil_y):
            for j in range(floor_x, ceil_x):
                if (i, j) == (floor_y, ceil_x - 1) or (i, j) == (
                        ceil_y - 1, floor_x) or not self.is_in_bound(j, i):
                    continue
                if (self.field[i][j].state != CellState.MISSED and
                        self.field[i][j].color != Color.RED):
                    self.field[i][j].color = color

    def change_color_death(self, x, y, prev_x, prev_y):
        ceil_y = y + 2
        floor_y = y - 1
        ceil_x = x + 2
        floor_x = x - 1
        for i in range(floor_y, ceil_y):
            for j in range(floor_x, ceil_x):
                if (i, j) == (floor_y, ceil_x - 1) or (i, j) == (
                        ceil_y - 1, floor_x) or not self.is_in_bound(j, i):
                    continue
                if self.field[i][j].state == CellState.DEAD:
                    if (self.field[i][j] != self.field[y][x] and
                            self.field[i][j] != self.field[prev_y][prev_x]):
                        self.change_color_death(j, i, x, y)
                elif self.field[y][x].state == CellState.DEAD:
                    if self.field[i][j].state != CellState.MISSED:
                        self.field[i][j].color = Color.RED
        return True

    def is_ship_dead(self, x, y, prev_x, prev_y):
        ceil_y = y + 2
        floor_y = y - 1
        ceil_x = x + 2
        floor_x = x - 1
        for i in range(floor_y, ceil_y):
            for j in range(floor_x, ceil_x):
                if (i, j) == (floor_y, ceil_x) or (i, j) == (
                        ceil_y, floor_x) or not self.is_in_bound(j, i):
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

    def place_ship_on_field(self, cells_to_take, player):
        taken_cells = []
        ship_len = len(cells_to_take)
        if not player.is_ship_in_hand(ship_len):
            return PlacementResult.LENGTH
        for (x, y) in cells_to_take:
            if not self.is_in_bound(x, y):
                return PlacementResult.UNABLE

            ceil_y = min(y + 2, self.side * 2 - 1)
            floor_y = max(y - 1, 0)
            ceil_x = min(x + 2, len(self.field[y]))
            floor_x = max(x - 1, 0)

            for i in range(floor_x, ceil_x):
                for j in range(floor_y, ceil_y):
                    if ((i == ceil_x and j == floor_y) or
                            (j == ceil_y and i == floor_x) or
                            not self.is_in_bound(i, j)):
                        continue
                    if ((self.field[j][i].state != CellState.EMPTY) and
                            self.field[j][i] not in taken_cells):
                        return PlacementResult.UNABLE
            taken_cells.append(self.field[y][x])
        for cell in taken_cells:
            self.change_color_hit(cell.x, cell.y, Color.RED)
            cell.state = CellState.SHIP
        player.move_ship_to_fleet(ship_len)
        for pos in cells_to_take:
            self.poses.remove(pos)
        if not player.hand:
            self.clear_colors()
        return PlacementResult.SUCCESS

    def auto_generate(self, hand, player):
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
                res = self.place_ship_on_field(cells_to_take, player)

                check_time = time.process_time()
                if check_time - start_time > 0.5:
                    return False
        return True

    def partition_auto_generate(self, hand, player):
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
                res = self.place_ship_on_field(cells_to_take, player)

                check_time = time.process_time()
                if check_time - start_time > 0.1:
                    return False

            if len(hand) == 1:
                self.auto_generate(hand, player)
                break

        return True


class BotAI:
    def __init__(self, difficulty):
        if difficulty > 1:
            raise ValueError
        self.diffs = [SimpleBotAI, HardBotAI]
        self.bot = self.diffs[difficulty]


class SimpleBotAI:
    def __init__(self, bot):
        self.field = bot.field
        self.bot = bot
        self.generator = lambda e: self.generate_bot_field(e)
        self.fire = lambda e: self.bot_fire(e)

    def generate_bot_field(self, env):
        print('Bot field is being generated')
        while not self.field.auto_generate(self.bot.hand, self.bot):
            env.reset_player_data(self.bot)
        print('Field was generated successfully')

    def bot_fire(self, env):
        result = ''
        _, enemy = env.get_nonactive_player()
        while result != FireResult.MISSED:
            y = random.randrange(self.bot.field.side * 2 - 1)
            x = random.randrange(len(enemy.field.field[y]))
            result = enemy.field.fire_cell(x, y, env, self.bot)
            if result != FireResult.UNABLE:
                print(PlayerType.BOT, result)


class HardBotAI:
    def __init__(self, bot):
        self.field = bot.field
        self.bot = bot
        self.generator = lambda e: self.generate_bot_field(e)
        self.fire = lambda e: self.bot_fire(e)
        self.last_fire = (-1, -1)

    def generate_bot_field(self, env):
        print('Bot field is being generated')
        while not self.field.partition_auto_generate(self.bot.hand, self.bot):
            env.reset_player_data(self.bot)
        print('Field was generated successfully')

    def bot_fire(self, env):
        result = ''
        _, enemy = env.get_nonactive_player()
        while result != FireResult.MISSED:
            if self.last_fire == (-1, -1):
                y = random.randrange(enemy.field.side * 2 - 1)
                x = random.randrange(len(enemy.field.field[y]))
                result = enemy.field.fire_cell(x, y, env, self.bot)
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
                result = enemy.field.fire_cell(x, y, env, self.bot)
            if result == FireResult.DESTROYED:
                self.last_fire = (-1, -1)
            elif result == FireResult.HIT:
                self.last_fire = (y, x)
            if result != FireResult.UNABLE:
                print(PlayerType.BOT, result)

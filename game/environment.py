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


class Player(enum.Enum):
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


class Environment:
    SHIP_MAX = 4
    DIFF = 0
    SIDE = 7

    def __init__(self, side=7, diff=0, ship_max=4):
        self.SHIP_MAX = ship_max
        self.DIFF = diff
        self.SIDE = side
        self.user_field = Honeycomb(side, Player.USER)
        self.bot_field = Honeycomb(side, Player.BOT)
        self.user_hand = [self.SHIP_MAX - x for x in range(self.SHIP_MAX)
                          for _ in range(x + 1)]
        self.bot_hand = [self.SHIP_MAX - x for x in range(self.SHIP_MAX)
                         for _ in range(x + 1)]
        self.user_fleet = 0
        self._bot_fleet = 0
        while sum(self.user_hand) / self.user_field.square > 0.3:
            self.SHIP_MAX -= 1
            self.user_hand = [self.SHIP_MAX - x for x in range(self.SHIP_MAX)
                              for _ in range(x + 1)]
            self.bot_hand = [self.SHIP_MAX - x for x in range(self.SHIP_MAX)
                             for _ in range(x + 1)]
        self.bot = BotAI(diff).bot(self.bot_field)
        self.bot.generator(self)

    def reset_player_data(self, player):
        if player == Player.USER:
            self.user_field = Honeycomb(self.SIDE, Player.USER)
            self.user_hand = [self.SHIP_MAX - x for x in range(self.SHIP_MAX)
                              for _ in range(x + 1)]
            self.user_fleet = 0
        else:
            self.bot_field = Honeycomb(self.SIDE, Player.BOT)
            self.bot_hand = [self.SHIP_MAX - x for x in range(self.SHIP_MAX)
                             for _ in range(x + 1)]
            self._bot_fleet = 0

    def generate_user_field(self):
        while not self.user_field.auto_generate(self.user_hand, self,
                                                Player.USER):
            self.reset_player_data(Player.USER)

    def is_player_defeated(self, player=Player.BOT):
        if player == Player.USER:
            return self.user_fleet == 0 and not self.user_hand
        return self._bot_fleet == 0 and not self.bot_hand

    def is_user_fleet_placed(self):
        return len(self.user_hand) == 0

    def is_ship_in_stack(self, ship_len, player=Player.BOT):
        stack = self.bot_hand
        if player == Player.USER:
            stack = self.user_hand
        for ship in stack:
            if ship == ship_len:
                return True
        return False

    def move_ship_to_fleet(self, ship_len, player=Player.BOT):
        stack = self.bot_hand
        if player == Player.USER:
            stack = self.user_hand
        for i in range(len(stack)):
            if stack[i] == ship_len:
                if player == Player.USER:
                    self.user_fleet += stack.pop(i)
                else:
                    self._bot_fleet += stack.pop(i)
                return True
        return False

    def delete_cell_from_fleet(self, player=Player.BOT):
        if player == Player.USER:
            self.user_fleet -= 1
        else:
            self._bot_fleet -= 1


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
                if (self.field[y][x].state, self.owner) == (
                        CellState.SHIP, Player.BOT):
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

    def fire_cell(self, x, y, env, player=Player.BOT):
        if not self.is_in_bound(x, y):
            return FireResult.UNABLE
        enemy = Player.USER
        if player == Player.USER:
            enemy = Player.BOT
        if self.field[y][x].state == CellState.SHIP:
            self.field[y][x].state = CellState.FIRED
            if player == Player.BOT:
                self.field[y][x].color = Color.RED
            else:
                self.field[y][x].color = Color.GREEN
            env.delete_cell_from_fleet(enemy)
            if self.is_ship_dead(x, y, x, y):
                if player == Player.USER:
                    self.change_color_death(x, y, x, y)
                return FireResult.DESTROYED
            else:
                if player == player.USER:
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

    def place_ship_on_field(self, cells_to_take, env, player=Player.BOT):
        taken_cells = []
        ship_len = len(cells_to_take)
        if not env.is_ship_in_stack(ship_len, player):
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
        env.move_ship_to_fleet(ship_len, player)
        for pos in cells_to_take:
            self.poses.remove(pos)
        if player == Player.USER and not env.user_hand:
            self.clear_colors()
        elif player == Player.BOT and not env.bot_hand:
            self.clear_colors()
        return PlacementResult.SUCCESS

    def auto_generate(self, hand, env, player):
        random.seed()
        start_time = time.process_time()
        while hand:
            ship_len = hand[0]
            res = ''
            while res != PlacementResult.SUCCESS:#"Ship was placed successfully!":
                rotation = random.choice(('vl', 'vr', 'h'))
                (x, y) = random.choice(self.poses)
                if rotation == 'vl':
                    cells_to_take = [(x, y + i) for i in range(ship_len)]
                elif rotation == 'vr':
                    cells_to_take = [(x + i, y + i) for i in range(ship_len)]
                else:
                    cells_to_take = [(x + i, y) for i in range(ship_len)]
                res = self.place_ship_on_field(cells_to_take, env, player)

                check_time = time.process_time()
                if check_time - start_time > 0.5:
                    return False
        return True

    def partition_auto_generate(self, hand, env, player):
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
            while res != PlacementResult.SUCCESS:#"Ship was placed successfully!":
                rotation = random.choice(('vl', 'vr', 'h'))
                y = random.randrange(min(y_border, self.side * 2 - 1))
                x = random.randrange(min(x_border, len(self.field[y])))
                if rotation == 'vl':
                    cells_to_take = [(x, y + i) for i in range(ship_len)]
                elif rotation == 'vr':
                    cells_to_take = [(x + i, y + i) for i in range(ship_len)]
                else:
                    cells_to_take = [(x + i, y) for i in range(ship_len)]
                res = self.place_ship_on_field(cells_to_take, env, player)

                check_time = time.process_time()
                if check_time - start_time > 0.1:
                    return False

            if len(hand) == 1:
                self.auto_generate(hand, env, player)
                break

        return True


class BotAI:
    def __init__(self, difficulty):
        if difficulty > 1:
            raise ValueError
        self.diffs = [SimpleBotAI, HardBotAI]
        self.bot = self.diffs[difficulty]


class SimpleBotAI:
    def __init__(self, field):
        self.field = field
        self.generator = lambda e: self.generate_bot_field(e)
        self.fire = lambda e: self.bot_fire(e)

    def generate_bot_field(self, env):
        print('Bot field is being generated')
        while not self.field.auto_generate(env.bot_hand, env, Player.BOT):
            env.reset_player_data(Player.BOT)
        print('Field was generated successfully')

    @staticmethod
    def bot_fire(env):
        result = ''
        while result != FireResult.MISSED:
            y = random.randrange(env.user_field.side * 2 - 1)
            x = random.randrange(len(env.user_field.field[y]))
            result = env.user_field.fire_cell(x, y, env)
            if result != FireResult.UNABLE:
                print(Player.BOT, result)


class HardBotAI:
    def __init__(self, field):
        self.field = field
        self.generator = lambda e: self.generate_bot_field(e)
        self.fire = lambda e: self.bot_fire(e)
        self.last_fire = (-1, -1)

    @staticmethod
    def generate_bot_field(env):
        print('Bot field is being generated')
        while not env.bot_field.partition_auto_generate(env.bot_hand, env,
                                                        Player.BOT):
            env.reset_player_data(Player.BOT)
        print('Field was generated successfully')

    def bot_fire(self, env):
        result = ''
        while result != FireResult.MISSED:
            if self.last_fire == (-1, -1):
                y = random.randrange(env.user_field.side * 2 - 1)
                x = random.randrange(len(env.user_field.field[y]))
                result = env.user_field.fire_cell(x, y, env)
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
                result = env.user_field.fire_cell(x, y, env)
            if result == FireResult.DESTROYED:
                self.last_fire = (-1, -1)
            elif result == FireResult.HIT:
                self.last_fire = (y, x)
            if result != FireResult.UNABLE:
                print(Player.BOT, result)

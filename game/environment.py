import enum
import random


class CellState(enum.Enum):
    NOT_FIELD = 0
    EMPTY = 1
    FIRED = 2
    DEAD = 3
    SHIP = 4
    MISSED = 5


class FireResult(enum.Enum):
    UNABLE = 0
    DESTROYED = 1
    HIT = 2
    MISSED = 3

    def __str__(self):
        res = self.name.lower()
        if self.name == 'UNABLE':
            res += ' to shoot there'
        elif self.name != 'MISSED':
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

    def __ne__(self, other):
        return (self.x, self.y) != (other.x, other.y)


class Environment:
    # TODO configurable fleet
    def __init__(self, side=7, ship_max=4):
        self.user_field = Honeycomb(side, Player.USER)
        self.bot_field = Honeycomb(side, Player.BOT)
        self._user_hand = [ship_max - x for x in range(ship_max) for _ in
                           range(x + 1)]
        self._bot_hand = [ship_max - x for x in range(ship_max) for _ in
                          range(x + 1)]
        self._user_fleet = 0
        self._bot_fleet = 0
        self._bot_fires = []  # TODO optimize bot's shooting
        self.generate_bot_field()

    def is_player_defeated(self, player=Player.BOT):
        if player == Player.USER:
            return self._user_fleet == 0 and not self._user_hand
        return self._bot_fleet == 0 and not self._bot_hand

    def is_user_fleet_placed(self):
        return len(self._user_hand) == 0

    def is_ship_in_stack(self, ship_len, player=Player.BOT):
        stack = self._bot_hand
        if player == Player.USER:
            stack = self._user_hand
        for ship in stack:
            if ship == ship_len:
                return True
        return False

    def move_ship_to_fleet(self, ship_len, player=Player.BOT):
        stack = self._bot_hand
        if player == Player.USER:
            stack = self._user_hand
        for i in range(len(stack)):
            if stack[i] == ship_len:
                if player == Player.USER:
                    self._user_fleet += stack.pop(i)
                else:
                    self._bot_fleet += stack.pop(i)
                return True
        return False

    def delete_cell_from_fleet(self, player=Player.BOT):
        if player == Player.USER:
            self._user_fleet -= 1
        else:
            self._bot_fleet -= 1

    def generate_bot_field(self):
        random.seed()
        while len(self._bot_hand) != 0:
            ship_len = random.choice(self._bot_hand)
            rotation = random.choice(('vl', 'vr', 'h'))
            y = random.randrange(self.bot_field.side * 2 - 1)
            x = random.randrange(len(self.bot_field.field[y]))
            if rotation == 'vl':
                cells_to_take = [(x, y + i) for i in range(ship_len)]
            elif rotation == 'vr':
                cells_to_take = [(x + i, y + i) for i in range(ship_len)]
            else:
                cells_to_take = [(x + i, y) for i in range(ship_len)]
            self.bot_field.place_ship_on_field(cells_to_take, self)

    def bot_fire(self):
        result = ''
        while result != FireResult.MISSED:
            y = random.randrange(self.user_field.side * 2 - 1)
            x = random.randrange(len(self.user_field.field[y]))
            result = self.user_field.fire_cell(x, y, self)
            if result != FireResult.UNABLE:
                print(Player.BOT, result)


class Honeycomb:
    def __init__(self, side, player):
        self.side = side
        self.field = []
        self.owner = player
        side_count = 0
        count = 0
        for y in range(side * 2 - 1):
            self.field.append([])
            for x in range(side + side_count):
                if y >= self.side - 1 and x < count:
                    self.field[y].append(Cell(x, y, CellState.NOT_FIELD))
                else:
                    self.field[y].append(Cell(x, y))
            if y < self.side - 1:
                side_count += 1
            else:
                count += 1

    def __str__(self):
        side_count = 0
        count = 0
        spaces_count = self.side * 2 - side_count
        res = ''
        for y in range(self.side * 2 - 1):
            res += ' ' * spaces_count
            for x in range(count, len(self.field[y])):
                if (self.field[y][x].state, self.owner) == (
                        CellState.SHIP, Player.USER):
                    res += 'S'
                elif self.field[y][x].state == CellState.FIRED:
                    res += 'F'
                elif self.field[y][x].state == CellState.DEAD:
                    res += 'D'
                elif self.field[y][x].state == CellState.MISSED:
                    res += 'M'
                elif self.field[y][x].state == CellState.NOT_FIELD:
                    res += ' '
                else:
                    res += 'X'
                res += '   '
            res += '\n'
            if y < self.side - 1:
                side_count += 1
                spaces_count -= 2
            else:
                count += 1
                spaces_count += 2
        return res

    def is_in_bound(self, x, y):
        global index
        if not 0 <= y < (self.side * 2 - 1):
            return False
        if x < self.side:
            return 0 <= x < len(self.field[y])

        for cell in self.field[y]:
            if cell.state != CellState.NOT_FIELD:
                index = self.field[y].index(cell)
                break
        return index <= x < len(self.field[y])

    def fire_cell(self, x, y, env, player=Player.BOT):
        if not self.is_in_bound(x, y):
            return FireResult.UNABLE # f'{player} can\'t shoot there!'
        enemy = Player.USER
        if player == Player.USER:
            enemy = Player.BOT
        if self.field[y][x].state == CellState.SHIP:
            self.field[y][x].state = CellState.FIRED
            env.delete_cell_from_fleet(enemy)
            if self.is_ship_dead(x, y, x, y):
                return FireResult.DESTROYED # f'{player} destroyed {enemy}\'s ship!'
            else:
                return FireResult.HIT # f'{player} hit {enemy}\'s ship!'
        elif self.field[y][x].state == CellState.EMPTY:
            self.field[y][x].state = CellState.MISSED
            return FireResult.MISSED # f'{player} missed!'
        else:
            return FireResult.UNABLE # f'{player} can\'t shoot there!'

    def is_ship_dead(self, x, y, prev_x, prev_y):
        ceil_y = min(y + 2, self.side * 2 - 1)
        floor_y = max(y - 1, 0)
        ceil_x = min(x + 2, len(self.field[y]))
        floor_x = max(x - 1, 0)
        for i in range(floor_y, ceil_y):
            for j in range(floor_x, ceil_x):
                if (i, j) == (floor_y, ceil_x) or (i, j) == (
                        ceil_y, floor_x) or not self.is_in_bound(j, i):
                    continue
                if self.field[i][j].state == CellState.FIRED:
                    if self.field[i][j] != self.field[y][x] and \
                            self.field[i][j] != self.field[prev_y][prev_x]:
                        if self.is_ship_dead(j, i, x, y):
                            continue
                        else:
                            return False
                elif self.field[i][j].state == CellState.SHIP:
                    return False
        self.field[y][x].state = CellState.DEAD
        return True

    def place_ship_on_field(self, cells_to_take, env, player=Player.BOT):
        taken_cells = []
        ship_len = len(cells_to_take)
        if not env.is_ship_in_stack(ship_len, player):
            return f"{player} doesn't have a ship with length {ship_len}"
        for (x, y) in cells_to_take:
            if not self.is_in_bound(x, y):
                return f"{player} can't place ship there!"

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
                    if (self.field[j][i].state != CellState.EMPTY and
                            self.field[j][i] not in taken_cells):
                        return f"{player} can't place ship there!"
            taken_cells.append(self.field[y][x])
        for cell in taken_cells:
            cell.state = CellState.SHIP
        env.move_ship_to_fleet(ship_len, player)
        return "Ship was placed successfully!"

from enum import *
import random


class CellState(Enum):
    not_field = 0
    empty = 1
    fired = 2
    dead = 3
    ship = 4
    missed = 5


class Cell:
    def __init__(self, x, y, state=CellState.empty):
        self.x = x
        self.y = y
        self.state = state

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y


class Environment:
    def __init__(self, side=7, ship_max=4):
        self.user_field = Honeycomb(side)
        self.bot_field = Honeycomb(side)
        self._user_hand = [ship_max - x for x in range(ship_max) for _ in
                           range(x + 1)]
        self._bot_hand = [ship_max - x for x in range(ship_max) for _ in
                          range(x + 1)]
        self._user_fleet = 0
        self._bot_fleet = 0
        self._bot_fires = []  # TODO optimize bot's shooting
        self.generate_bot_field()

    def is_player_defeated(self, player):
        if player == 'user':
            return self._user_fleet == 0 and len(self._user_hand) == 0
        return self._bot_fleet == 0 and len(self._bot_hand) == 0

    def is_user_fleet_placed(self):
        return len(self._user_hand) == 0

    def is_ship_in_stack(self, ship_len, player):
        stack = self._bot_hand
        if player == 'user':
            stack = self._user_hand
        for ship in stack:
            if ship == ship_len:
                return True
        return False

    def move_ship_to_fleet(self, ship_len, player):
        stack = self._bot_hand
        if player == 'user':
            stack = self._user_hand
        for i in range(len(stack)):
            if stack[i] == ship_len:
                if player == 'user':
                    self._user_fleet += stack.pop(i)
                else:
                    self._bot_fleet += stack.pop(i)
                return True
        return False

    def delete_cell_from_fleet(self, player):
        if player == 'user':
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
            self.bot_field.place_ship_on_field(cells_to_take, self, 'bot')

    def bot_fire(self):
        result = ''
        while result != 'bot missed!':
            y = random.randrange(self.user_field.side * 2 - 1)
            x = random.randrange(len(self.user_field.field[y]))
            result = self.user_field.fire_cell(x, y, self, 'bot')
            if result != "bot can't shoot there!":
                print(result)


class Honeycomb:
    def __init__(self, side):
        self.side = side
        self.field = []
        side_count = 0
        count = 0
        for y in range(side * 2 - 1):
            self.field.append([])
            for x in range(side + side_count):
                if y >= self.side - 1 and x < count:
                    self.field[y].append(Cell(x, y, CellState.not_field))
                else:
                    self.field[y].append(Cell(x, y))
            if y < self.side - 1:
                side_count += 1
            else:
                count += 1

    def is_in_bound(self, x, y):
        if not 0 <= y < (self.side * 2 - 1):
            return False
        if x < self.side:
            return 0 <= x < len(self.field[y])
        else:
            for cell in self.field[y]:
                if cell.state != CellState.not_field:
                    index = self.field[y].index(cell)
                    break
            return index <= x < len(self.field[y])

    def fire_cell(self, x, y, env, player):
        if not self.is_in_bound(x, y):
            return f'{player} can\'t shoot there!'
        enemy = 'user'
        if player == 'user':
            enemy = 'bot'
        if self.field[y][x].state == CellState.ship:
            self.field[y][x].state = CellState.fired
            env.delete_cell_from_fleet(enemy)
            if self.is_ship_dead(x, y, x, y):
                return f'{player} destroyed {enemy}\'s ship!'
            else:
                return f'{player} hit {enemy}\'s ship!'
        elif self.field[y][x].state == CellState.empty:
            self.field[y][x].state = CellState.missed
            return f'{player} missed!'
        else:
            return f'{player} can\'t shoot there!'

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
                if self.field[i][j].state == CellState.fired:
                    if self.field[i][j] != self.field[y][x] and \
                            self.field[i][j] != self.field[prev_y][prev_x]:
                        if self.is_ship_dead(j, i, x, y):
                            continue
                        else:
                            return False
                elif self.field[i][j].state == CellState.ship:
                    return False
        self.field[y][x].state = CellState.dead
        return True

    def place_ship_on_field(self, cells_to_take, env, player):
        taken_cells = []
        ship_len = len(cells_to_take)
        if not env.is_ship_in_stack(ship_len, player):
            return f"{player} don't have a ship with length {cells_to_take}"
        for (x, y) in cells_to_take:
            if not self.is_in_bound(x, y):
                return f"{player} can't place the ship here!"

            ceil_y = min(y + 2, self.side * 2 - 1)
            floor_y = max(y - 1, 0)
            ceil_x = min(x + 2, len(self.field[y]))
            floor_x = max(x - 1, 0)

            for i in range(floor_x, ceil_x):
                for j in range(floor_y, ceil_y):
                    if (i == ceil_x and j == floor_y) or (
                            j == ceil_y and i == floor_x
                    ) or not self.is_in_bound(i, j):
                        continue
                    if self.field[j][i].state != CellState.empty and \
                            self.field[j][i] not in taken_cells:
                        return f"{player} can't place the ship here!"
            taken_cells.append(self.field[y][x])
        for cell in taken_cells:
            cell.state = CellState.ship
        env.move_ship_to_fleet(ship_len, player)
        return "ship was placed successfully!"

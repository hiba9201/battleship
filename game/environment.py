#! /bin/local/python3
from enum import *
import random


class Environment:
    def __init__(self, m, n):
        self.user_field = Field(m, n)
        self.bot_field = Field(m, n)
        self._user_stack = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self._bot_stack = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self._user_fleet = 0
        self._bot_fleet = 0
        self._bot_fires = []
        self.generate_bot_field()

    def is_ship_in_stack(self, ship_len, player):
        stack = self._bot_stack
        if player == 'user':
            stack = self._user_stack
        for ship in stack:
            if ship == ship_len:
                return True
        return False

    def move_ship_to_fleet(self, ship_len, player):
        stack = self._bot_stack
        if player == 'user':
            stack = self._user_stack
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
        while len(self._bot_stack) != 0:
            ship = random.choice(self._bot_stack)
            rotation = random.choice(['ver', 'hor'])
            x = random.randrange(self.bot_field.width)
            y = random.randrange(self.bot_field.height)
            cells_to_take = []
            if rotation == 'ver':
                for i in range(ship):
                    cells_to_take.append((x, y + i))
            elif rotation == 'hor':
                for i in range(ship):
                    cells_to_take.append((x + i, y))
            self.bot_field.place_ship_on_field(cells_to_take, self, 'bot')

    def random_fire(self):
        result = ''
        while result != 'You missed!':
            x = random.randrange(self.user_field.width)
            y = random.randrange(self.user_field.height)
            result = self.user_field.fire_cell(x, y, self)


# TODO all methods return strings, not print them
class Field:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.field = []
        for x in range(width):
            self.field.append([])
            for y in range(height):
                self.field[x].append(Cell(x, y))

    def fire_cell(self, x, y, env):
        if self.field[x][y].state == CellState.ship:
            self.field[x][y].state = CellState.fired
            env.delete_cell_from_fleet('bot')
            if self.is_ship_dead(x, y, x, y):
                return 'You destroyed bot\'s ship!'
            else:
                return 'You hit the bot\'s ship!'
        elif self.field[x][y].state == CellState.empty:
            self.field[x][y].state = CellState.missed
            return 'You missed!'
        else:
            return 'You can\'t shoot there!'

    def is_ship_dead(self, x, y, prev_x, prev_y):
        ceil_x = min(x + 2, self.width)
        floor_x = max(x - 1, 0)
        ceil_y = min(y + 2, self.height)
        floor_y = max(y - 1, 0)
        for i in range(floor_x, ceil_x):
            for j in range(floor_y, ceil_y):
                if self.field[i][j].state == CellState.fired:
                    if self.field[i][j] != self.field[x][y] and self.field[i][
                            j] != self.field[prev_x][prev_y]:
                        if self.is_ship_dead(i, j, x, y):
                            continue
                        else:
                            return False
                elif self.field[i][j].state == CellState.ship:
                    return False
        self.field[x][y].state = CellState.dead
        return True

    def place_ship_on_field(self, cells_to_take, env, player):
        taken_cells = []
        ship_len = len(cells_to_take)
        if not env.is_ship_in_stack(ship_len, player):
            return "You don't have a ship with length {}".format(
                len(cells_to_take))
        for (x, y) in cells_to_take:
            if x >= self.width or y >= self.height:
                return "You can't place the ship here!"
            ceil_x = min(x + 2, self.width)
            floor_x = max(x - 1, 0)
            ceil_y = min(y + 2, self.height)
            floor_y = max(y - 1, 0)
            for i in range(floor_x, ceil_x):
                for j in range(floor_y, ceil_y):
                    if self.field[i][j].state != CellState.empty and \
                            self.field[i][j] not in taken_cells:
                        return "You can't place the ship here!"
            taken_cells.append(self.field[x][y])
        for cell in taken_cells:
            cell.state = CellState.ship
        env.move_ship_to_fleet(ship_len, player)
        return "Ship was placed successfully!"


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = CellState.empty

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y


class Ship:
    def __init__(self, length):
        self.length = length
        self.rotation = Rotation.vertical

    def rotate(self):
        self.rotation = Rotation(self.rotation % 2 + 1)


class CellState(Enum):
    empty = 1
    fired = 2
    dead = 3
    ship = 4
    missed = 5


class Rotation(IntEnum):
    vertical = 1
    horizontal = 2

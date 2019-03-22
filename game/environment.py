#! /bin/local/python3
from enum import *


class Environment:
    def __init__(self, m, n):
        self.user_field = Field(m, n)
        self.bot_field = Field(m, n)
        self.user_stack = [Ship(4), Ship(3), Ship(3), Ship(2), Ship(2),
                           Ship(2), Ship(1), Ship(1), Ship(1), Ship(1)]
        self.bot_stack = [Ship(4), Ship(3), Ship(3), Ship(2), Ship(2), Ship(2),
                          Ship(1), Ship(1), Ship(1), Ship(1)]
        self.user_fleet = []
        self.bot_fleet = []
        self.bot_field.generate_bot_field()

    def is_ship_in_user_stack(self, ship_len):
        for ship in self.user_stack:
            if ship.length == ship_len:
                return True
        return False

    def is_ship_in_bot_stack(self, ship_len):
        for ship in self.bot_stack:
            if ship.length == ship_len:
                return True
        return False

    def move_user_ship_to_fleet(self, ship_len):
        for i in range(len(self.user_stack)):
            if self.user_stack[i].length == ship_len:
                self.user_fleet.append(self.user_stack.pop(i))
                return True
        return False


class Field:
    def __init__(self, width, high):
        self.width = width
        self.high = high
        self.field = []
        for x in range(width):
            self.field.append([])
            for y in range(high):
                self.field[x].append(Cell(x, y))

    def place_ship_on_field(self, cells_to_take, env):
        taken_cells = []
        ship_len = len(cells_to_take)
        if not env.is_ship_in_user_stack(ship_len):
            print("You don't have a ship with length {}".format(
                len(cells_to_take)))
            return "Not OK"
        for (x, y) in cells_to_take:
            ceil_x = min(x + 2, self.width)
            floor_x = max(x - 1, 0)
            ceil_y = min(y + 2, self.high)
            floor_y = max(y - 1, 0)
            for i in range(floor_x, ceil_x):
                for j in range(floor_y, ceil_y):
                    if self.field[i][j].state != CellState.empty and \
                            self.field[i][j] not in taken_cells:
                        print("You can't place the ship here!")
                        return "Not OK"
            taken_cells.append(self.field[x][y])
        for cell in taken_cells:
            cell.state = CellState.taken
        env.move_user_ship_to_fleet(ship_len)
        print("Ship was placed successfully!")
        return "OK"

    def generate_bot_field(self):
        pass


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = CellState.empty


class Ship:
    def __init__(self, length):
        self.length = length
        self.rotation = Rotation.vertical

    def __mul__(self, const):
        res = []
        for i in range(const):
            res.append(self)
        return res

    def __str__(self):
        return "'{}'".format(self.length)

    def rotate(self):
        self.rotation = Rotation(self.rotation % 2 + 1)


class CellState(Enum):
    empty = 1
    fired = 2
    dead = 3
    taken = 4
    missed = 5


class Rotation(IntEnum):
    vertical = 1
    horizontal = 2

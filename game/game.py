#! /bin/local/python3
import math


class Game:
    def __init__(self):
        self.user_field = Field()
        self.bot_field = Field()
        self.user_fleet = [Ship(4), Ship(3) * 2, Ship(2) * 3, Ship(1) * 4]
        self.bot_fleet = [Ship(4), Ship(3) * 2, Ship(2) * 3, Ship(1) * 4]


class Field:
    def __init__(self):
        self.field = []

    def add_cells(self, *cells):
        for cell in cells:
            self.field.append(cell)

    def place_ship_on_field(self, ship, *cells_to_take):
        for cell in cells_to_take:
            for taken_cell in self.field:
                if cell.is_cell_near(
                        taken_cell) and taken_cell not in cells_to_take:
                    return "You can't place the ship {} here".format(ship)
            self.add_cells(cell)
        return "OK"


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_cell_near(self, other):
        if math.fabs(other.x - self.x) <= 1 and math.fabs(
                other.y - self.y) <= 1:
            return True
        return False


class Ship:
    def __init__(self, length):
        self.length = length

    def __mul__(self, const):
        res = []
        for i in range(const):
            res.append(self)
        return res

    def __str__(self):
        return "'{}'".format(self.length)

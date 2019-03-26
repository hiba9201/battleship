import unittest
from game.environment import *


# TODO rewrite tests
class CellTest(unittest.TestCase):
    pass


class FieldTest(unittest.TestCase):
    def test_place_1_ship(self):
        field = Field(5, 5)
        field.field[1][1].state = CellState.ship
        self.assertNotEqual(field.place_ship_on_field([(0, 0)], ),
                            "OK")
        self.assertEqual(field.place_ship_on_field([(1, 3)]), "OK")

    def test_place_2_ship(self):
        field = Field(5, 5)
        field.field[1][1].state = CellState.ship
        self.assertNotEqual(
            field.place_ship_on_field([(0, 0), (0, 1)]), "OK")
        self.assertEqual(
            field.place_ship_on_field([(1, 3), (2, 3)]), "OK")


class ShipTests(unittest.TestCase):
    def test_multiply(self):
        self.assertEqual(len(Ship(2) * 3), 3)

    def test_rotation(self):
        ship = Ship(2)
        ship.rotate()
        self.assertEqual(Rotation.horizontal, ship.rotation)
        ship.rotate()
        self.assertEqual(Rotation.vertical, ship.rotation)


if __name__ == '__main__':
    unittest.main()

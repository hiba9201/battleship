import unittest
from game.game import *


class CellTest(unittest.TestCase):
    def test_is_cell_near(self):
        tested_cell = Cell(2, 2)
        self.assertTrue(tested_cell.is_cell_near(Cell(1, 2)))
        self.assertTrue(tested_cell.is_cell_near(Cell(2, 2)))
        self.assertTrue(tested_cell.is_cell_near(Cell(1, 1)))
        self.assertFalse(tested_cell.is_cell_near(Cell(0, 2)))


class FieldTest(unittest.TestCase):
    def test_place_1_ship(self):
        field = Field()
        field.add_cells(Cell(1, 1))
        self.assertNotEqual(field.place_ship_on_field(Ship(1), Cell(0, 0)),
                            "OK")
        self.assertEqual(field.place_ship_on_field(Ship(1), Cell(1, 3)), "OK")
        self.assertEqual(2, len(field.field))

    def test_place_2_ship(self):
        field = Field()
        field.add_cells(Cell(1, 1))
        self.assertNotEqual(
            field.place_ship_on_field(Ship(2), Cell(0, 0), Cell(0, 1)), "OK")
        self.assertEqual(
            field.place_ship_on_field(Ship(2), Cell(1, 3), Cell(2, 3)), "OK")
        self.assertEqual(3, len(field.field))

    def test_add_cell(self):
        field = Field()
        field.add_cells(Cell(0, 0))
        self.assertEqual(len(field.field), 1)


class ShipTests(unittest.TestCase):
    def test_multiply(self):
        self.assertEqual(len(Ship(2) * 3), 3)


if __name__ == '__main__':
    unittest.main()

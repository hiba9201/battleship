import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

from game.environment import (Honeycomb, Environment, Cell, CellState, PlayerType,
                              FireResult, PlacementResult)


class CellTest(unittest.TestCase):
    def test_not_equal(self):
        first = Cell(1, 1)
        second = Cell(1, 2)
        third = Cell(1, 1)
        self.assertNotEqual(first, second)
        self.assertFalse(first != third)


class EnvironmentTest(unittest.TestCase):
    def test_player_defeated(self):
        env = Environment(3, ship_max=1)
        env.user_field.place_ship_on_field([(0, 0)], env, PlayerType.USER)
        self.assertFalse(env.is_player_defeated(PlayerType.USER))
        env.user_field.fire_cell(0, 0, env)
        self.assertTrue(env.is_player_defeated(PlayerType.USER))

    def test_fleet_placement(self):
        env = Environment(3, ship_max=1)
        self.assertFalse(env.is_fleet_placed())
        env.user_field.place_ship_on_field([(0, 0)], env, PlayerType.USER)
        self.assertTrue(env.is_fleet_placed())

    def test_player_have_ship_on_hands(self):
        env = Environment(3, ship_max=1)
        self.assertFalse(env.is_ship_in_stack(2, PlayerType.USER))
        self.assertTrue(env.is_ship_in_stack(1, PlayerType.USER))
        env.user_field.place_ship_on_field([(0, 0)], env, PlayerType.USER)
        self.assertFalse(env.is_ship_in_stack(1, PlayerType.USER))


class HoneycombTest(unittest.TestCase):
    def test_num_to_letter(self):
        self.assertEqual('A', Honeycomb.number_to_letters(0))
        self.assertEqual('C', Honeycomb.number_to_letters(2))
        self.assertEqual('AB', Honeycomb.number_to_letters(27))
        self.assertEqual('AOC', Honeycomb.number_to_letters(1068))

    def test_place_1_ship(self):
        env = Environment(5, ship_max=2)
        env.user_field.field[1][1].state = CellState.SHIP
        self.assertNotEqual(
            env.user_field.place_ship_on_field([(0, 0)], env, PlayerType.USER),
            PlacementResult.SUCCESS)
        self.assertEqual(
            env.user_field.place_ship_on_field([(1, 3)], env, PlayerType.USER),
            PlacementResult.SUCCESS)

    def test_place_2_ship(self):
        env = Environment(5, ship_max=2)
        env.user_field.field[1][1].state = CellState.SHIP
        self.assertNotEqual(
            env.user_field.place_ship_on_field([(0, 0), (0, 1)], env,
                                               PlayerType.USER),
            PlacementResult.SUCCESS)
        self.assertEqual(
            env.user_field.place_ship_on_field([(1, 3), (2, 3)], env,
                                               PlayerType.USER),
            PlacementResult.SUCCESS)

    def test_bound(self):
        field = Honeycomb(3, PlayerType.USER)
        self.assertTrue(field.is_in_bound(1, 1))
        self.assertFalse(field.is_in_bound(4, 1))
        self.assertFalse(field.is_in_bound(-1, 1))
        self.assertFalse(field.is_in_bound(4, 6))

    def test_fire_not_destroyed(self):
        env = Environment(5, ship_max=2)
        env.user_field.place_ship_on_field([(0, 0), (0, 1)], env, PlayerType.USER)
        state = env.user_field.fire_cell(0, 0, env)
        self.assertFalse(env.is_player_defeated(PlayerType.USER))
        self.assertEqual(state, FireResult.HIT)

    def test_fire_destroyed(self):
        env = Environment(5, ship_max=1)
        env.user_field.place_ship_on_field([(0, 0)], env, PlayerType.USER)
        state = env.user_field.fire_cell(0, 0, env)
        self.assertTrue(env.is_player_defeated(PlayerType.USER))
        self.assertEqual(state, FireResult.DESTROYED)


if __name__ == '__main__':
    unittest.main()

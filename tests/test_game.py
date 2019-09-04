import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

from game.environment import (Honeycomb, Environment, Cell, CellState,
                              PlayerType, Player,
                              FireResult, PlacementResult)
from game.utils import Utils


class CellTest(unittest.TestCase):
    def test_not_equal(self):
        first = Cell(1, 1)
        second = Cell(1, 2)
        third = Cell(1, 1)
        self.assertNotEqual(first, second)
        self.assertFalse(first != third)


class EnvironmentTest(unittest.TestCase):
    def test_player_defeated(self):
        env = Environment(3, 0, 1)
        env.add_player(PlayerType.USER, 'user')
        env.players['user'].field.place_ship_on_field([(1, 0)])
        self.assertFalse(env.players['user'].is_player_defeated())
        env.players['user'].field.fire_cell(1, 0, Player(PlayerType.BOT, env))
        self.assertTrue(env.players['user'].is_player_defeated())

    def test_fleet_placement(self):
        env = Environment(3, 0, 1)
        env.add_player(PlayerType.USER, 'user')
        self.assertFalse(env.players['user'].is_fleet_placed())
        env.players['user'].field.place_ship_on_field([(1, 0)])
        self.assertTrue(env.players['user'].is_fleet_placed())

    def test_player_have_ship_on_hands(self):
        env = Environment(3, 0, 1)
        env.add_player(PlayerType.USER, 'user')
        self.assertFalse(env.players['user'].is_ship_in_hand(2))
        self.assertTrue(env.players['user'].is_ship_in_hand(1))
        env.players['user'].field.place_ship_on_field([(1, 0)])
        self.assertFalse(env.players['user'].is_ship_in_hand(1))


class UtilsTest(unittest.TestCase):
    def test_num_to_letter(self):
        self.assertEqual('A', Utils.number_to_letters(0))
        self.assertEqual('C', Utils.number_to_letters(2))
        self.assertEqual('AB', Utils.number_to_letters(27))
        self.assertEqual('AOC', Utils.number_to_letters(1068))


class HoneycombTest(unittest.TestCase):
    def test_place_1_ship(self):
        env = Environment(5, 0, 2)
        env.add_player(PlayerType.USER, 'user')
        env.players['user'].field.field[1][1].state = CellState.SHIP
        self.assertNotEqual(
            env.players['user'].field.place_ship_on_field([(0, 1)]),
            PlacementResult.SUCCESS)
        self.assertEqual(
            env.players['user'].field.place_ship_on_field([(1, 3)]),
            PlacementResult.SUCCESS)

    def test_place_2_ship(self):
        env = Environment(5, 0, 2)
        env.add_player(PlayerType.USER, 'user')
        env.players['user'].field.field[1][1].state = CellState.SHIP
        self.assertNotEqual(
            env.players['user'].field.place_ship_on_field([(0, 0), (0, 1)]),
            PlacementResult.SUCCESS)
        self.assertEqual(
            env.players['user'].field.place_ship_on_field([(1, 3), (2, 3)]),
            PlacementResult.SUCCESS)

    def test_bound(self):
        env = Environment(3, 0, 1)
        field = Honeycomb(3, Player(PlayerType.USER, env), env)
        self.assertTrue(field.is_in_bound(1, 1))
        self.assertFalse(field.is_in_bound(4, 1))
        self.assertFalse(field.is_in_bound(-1, 1))
        self.assertFalse(field.is_in_bound(4, 6))

    def test_fire_not_destroyed(self):
        env = Environment(5, 0, 2)
        env.add_player(PlayerType.USER, 'user')
        env.players['user'].field.place_ship_on_field([(0, 2), (0, 1)])
        state = env.players['user'].field.fire_cell(0, 2,
                                                    Player(PlayerType.BOT,
                                                           env))
        self.assertFalse(env.players['user'].is_player_defeated())
        self.assertEqual(FireResult.HIT, state)

    def test_fire_destroyed(self):
        env = Environment(5, 0, 1)
        env.add_player(PlayerType.USER, 'user')
        env.players['user'].field.place_ship_on_field([(0, 1)])
        state = env.players['user'].field.fire_cell(0, 1,
                                                    Player(PlayerType.BOT,
                                                           env))
        self.assertTrue(env.players['user'].is_player_defeated())
        self.assertEqual(FireResult.DESTROYED, state)


if __name__ == '__main__':
    unittest.main()

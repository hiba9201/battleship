import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

from game.environment import (Honeycomb, Environment, Cell, CellState,
                              PlayerType, Player,
                              FireResult, PlacementResult)
from game.utils import Utils, TwitterUtils


class CellTest(unittest.TestCase):
    def test_not_equal(self):
        first = Cell(1, 1)
        second = Cell(1, 2)
        third = Cell(1, 1)
        self.assertNotEqual(first, second)
        self.assertFalse(first != third)


class PlayerTest(unittest.TestCase):
    def test_bot_init_diff_right(self):
        env = Environment(3, 0, 2)
        env.add_player(PlayerType.BOT, 'bot')
        self.assertEqual(env.players['bot'].AI.diff, env.diff)

    def test_bot_init_diff_wrong(self):
        env = Environment(3, 100, 2)
        env.add_player(PlayerType.BOT, 'bot')
        self.assertEqual(env.players['bot'].AI.diff, env.diff)
        self.assertEqual(env.diff, 0)

    def test_ship_in_hand(self):
        env = Environment(3, 0, 2)
        env.add_player(PlayerType.USER, 'user')
        self.assertTrue(env.players['user'].is_ship_in_hand(1))
        env.players['user'].field.place_ship_on_field([(0, 1)])
        self.assertTrue(env.players['user'].is_ship_in_hand(1))
        env.players['user'].field.place_ship_on_field([(3, 4)])
        self.assertFalse(env.players['user'].is_ship_in_hand(1))

    def test_is_fleet_placed(self):
        env = Environment(3, 0, 1)
        env.add_player(PlayerType.USER, 'user')
        self.assertFalse(env.players['user'].is_fleet_placed())
        env.players['user'].field.place_ship_on_field([(0, 1)])
        self.assertTrue(env.players['user'].is_fleet_placed())

    def test_move_to_fleet(self):
        env = Environment(3, 0, 1)
        env.add_player(PlayerType.USER, 'user')
        env.players['user'].move_ship_to_fleet(1)
        self.assertEqual(env.players['user'].fleet, 1)
        self.assertNotIn(1, env.players['user'].hand)

    def test_delete_from_fleet(self):
        env = Environment(3, 0, 1)
        env.add_player(PlayerType.USER, 'user')
        env.players['user'].move_ship_to_fleet(1)
        env.players['user'].delete_cell_from_fleet()
        self.assertEqual(0, env.players['user'].fleet)


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

    def test_coding(self):
        coded = TwitterUtils.code('abc123', 'aa2a')
        decoded = TwitterUtils.decode(coded, 'aa2a')
        self.assertEqual('abc123', decoded)


class HoneycombTest(unittest.TestCase):
    def test_place_corner_ship_small_field(self):
        env = Environment(3, 0, 1)
        env.add_player(PlayerType.USER, 'user')
        self.assertEqual(
            env.players['user'].field.place_ship_on_field([(0, 0)]),
            PlacementResult.UNABLE)
        self.assertEqual(
            env.players['user'].field.place_ship_on_field([(0, 1)]),
            PlacementResult.SUCCESS)

    def test_place_corner_ship_big_field(self):
        env = Environment(6, 0, 4)
        env.add_player(PlayerType.USER, 'user')
        self.assertEqual(
            env.players['user'].field.place_ship_on_field([(0, 0)]),
            PlacementResult.SUCCESS)
        self.assertEqual(
            env.players['user'].field.place_ship_on_field([(0, 5)]),
            PlacementResult.UNABLE)

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

    def test_fire_twice(self):
        env = Environment(5, 0, 1)
        env.add_player(PlayerType.USER, 'user')
        state = env.players['user'].field.fire_cell(0, 1,
                                                    Player(PlayerType.BOT,
                                                           env))
        self.assertEqual(state, FireResult.MISSED)
        state = env.players['user'].field.fire_cell(0, 1,
                                                    Player(PlayerType.BOT,
                                                           env))
        self.assertEqual(state, FireResult.UNABLE)

    def test_fire_out_of_field(self):
        env = Environment(5, 0, 1)
        env.add_player(PlayerType.USER, 'user')
        state = env.players['user'].field.fire_cell(0, 6,
                                                    Player(PlayerType.BOT,
                                                           env))
        self.assertEqual(state, FireResult.UNABLE)

        if __name__ == '__main__':
            unittest.main()

import unittest
from game.environment import *


class CellTest(unittest.TestCase):
    def test_not_equal(self):
        first = Cell(1, 1)
        second = Cell(1, 2)
        third = Cell(1, 1)
        self.assertTrue(first != second)
        self.assertFalse(first != third)


class EnvironmentTest(unittest.TestCase):
    def test_player_defeated(self):
        env = Environment(3, 1)
        env.user_field.place_ship_on_field([(0, 0)], env, 'user')
        self.assertFalse(env.is_player_defeated('user'))
        env.user_field.fire_cell(0, 0, env, 'bot')
        self.assertTrue(env.is_player_defeated('user'))

    def test_fleet_placement(self):
        env = Environment(3, 1)
        self.assertFalse(env.is_user_fleet_placed())
        env.user_field.place_ship_on_field([(0, 0)], env, 'user')
        self.assertTrue(env.is_user_fleet_placed())

    def test_player_have_ship_on_hands(self):
        env = Environment(3, 1)
        self.assertFalse(env.is_ship_in_stack(2, 'user'))
        self.assertTrue(env.is_ship_in_stack(1, 'user'))
        env.user_field.place_ship_on_field([(0, 0)], env, 'user')
        self.assertFalse(env.is_ship_in_stack(1, 'user'))


class HoneycombTest(unittest.TestCase):
    def test_place_1_ship(self):
        env = Environment(5)
        env.user_field.field[1][1].state = CellState.ship
        self.assertNotEqual(
            env.user_field.place_ship_on_field([(0, 0)], env, 'user'),
            "ship was placed successfully!")
        self.assertEqual(
            env.user_field.place_ship_on_field([(1, 3)], env, 'user'),
            "ship was placed successfully!")

    def test_place_2_ship(self):
        env = Environment(5)
        env.user_field.field[1][1].state = CellState.ship
        self.assertNotEqual(
            env.user_field.place_ship_on_field([(0, 0), (0, 1)], env, 'user'),
            "ship was placed successfully!")
        self.assertEqual(
            env.user_field.place_ship_on_field([(1, 3), (2, 3)], env, 'user'),
            "ship was placed successfully!")

    def test_bound(self):
        field = Honeycomb(3)
        self.assertTrue(field.is_in_bound(1, 1))
        self.assertFalse(field.is_in_bound(4, 1))
        self.assertFalse(field.is_in_bound(-1, 1))
        self.assertFalse(field.is_in_bound(4, 6))

    def test_fire_not_destroyed(self):
        env = Environment(5)
        env.user_field.place_ship_on_field([(0, 0), (0, 1)], env, 'user')
        state = env.user_field.fire_cell(0, 0, env, 'bot')
        self.assertFalse(env.is_player_defeated('user'))
        self.assertEqual(state, "bot hit user's ship!")

    def test_fire_destroyed(self):
        env = Environment(5, 1)
        env.user_field.place_ship_on_field([(0, 0)], env, 'user')
        state = env.user_field.fire_cell(0, 0, env, 'bot')
        self.assertTrue(env.is_player_defeated('user'))
        self.assertEqual(state, "bot destroyed user's ship!")


if __name__ == '__main__':
    unittest.main()

import ast
from pathlib import Path
import unittest
from racing_controller import Driver


def sensor(**overrides):
    state = dict(speedX=60, speedY=0, rpm=5000, angle=0, trackPos=0,
                 track=[100] * 19, wheelSpinVel=[50] * 4)
    state.update(overrides)
    return state


class DriverTests(unittest.TestCase):
    def test_brakes_for_reduced_visibility_without_throttle(self):
        action = Driver().step(sensor(speedX=100, track=[15] * 19))
        self.assertGreater(action['brake'], 0)
        self.assertEqual(action['accel'], 0)

    def test_steering_symmetry_and_rate_bound(self):
        left = Driver().step(sensor(angle=.2, trackPos=-.3, speedY=-2))
        right = Driver().step(sensor(angle=-.2, trackPos=.3, speedY=2))
        self.assertAlmostEqual(left['steer'], -right['steer'])
        self.assertLessEqual(abs(left['steer']), .06)

    def test_shift_dwell_and_hysteresis(self):
        driver = Driver()
        self.assertEqual(driver.step(sensor(rpm=8000))['gear'], 2)
        for _ in range(30):
            self.assertEqual(driver.step(sensor(rpm=3000))['gear'], 2)
        for _ in range(200):
            self.assertEqual(driver.step(sensor(rpm=5000))['gear'], 2)

    def test_no_simultaneous_brake_throttle_or_out_of_range_commands(self):
        driver = Driver()
        for speed in range(0, 250, 5):
            for heading in (-3, -.3, 0, .3, 3):
                action = driver.step(sensor(speedX=speed, angle=heading))
                self.assertTrue(-1 <= action['steer'] <= 1)
                self.assertTrue(0 <= action['accel'] <= 1)
                self.assertTrue(0 <= action['brake'] <= 1)
                self.assertFalse(action['accel'] and action['brake'])

    def test_single_main_entry_point(self):
        source = Path(__file__).with_name('torcs_jm_par.py').read_text()
        tree = ast.parse(source)
        main_blocks = [n for n in tree.body if isinstance(n, ast.If)
                       and '__name__' in ast.unparse(n.test)]
        self.assertEqual(len(main_blocks), 1)
        self.assertIn('run_controller(drive_mapped_v2_r1)', ast.unparse(main_blocks[0]))


if __name__ == '__main__':
    unittest.main()

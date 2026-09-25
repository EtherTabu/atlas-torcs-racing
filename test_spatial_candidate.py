"""Offline checks of the experimental candidate and spatial accounting."""
import json
from pathlib import Path
import unittest

from experimental_controller import Driver
from lap_delta import load, segments, REFERENCE
from torcs_jm_par import DriverAction

ROOT = Path(__file__).resolve().parent
BEST = ROOT / 'experiments/20260924T182501_227244Z_experimental-v3'


class SpatialCandidateTests(unittest.TestCase):
    def test_recorded_actions_replay_exactly(self):
        driver = Driver(json.loads((BEST / 'parameters.json').read_text()))
        for row in load(BEST):
            action = DriverAction()
            action.d.update(driver.step(row['s']))
            from analyze_run import parse
            self.assertEqual(parse(repr(action)), row['a'])

    def test_line_knots_have_continuous_heading(self):
        driver = Driver(json.loads((BEST / 'parameters.json').read_text()))
        for distance, target in driver.p['line_points']:
            self.assertAlmostEqual(driver.line(distance)[0], target)
            self.assertAlmostEqual(driver.line(distance)[1], 0)
            for offset in [-1e-6, 1e-6]:
                self.assertAlmostEqual(driver.line(distance + offset)[0], target, places=6)
                self.assertAlmostEqual(driver.line(distance + offset)[1], 0, places=6)

    def test_spatial_time_reconciles_with_official_timer(self):
        for run, expected in [(BEST, 89.394), (REFERENCE, 95.310)]:
            rows = segments(load(run))
            self.assertEqual(len(rows), 11)
            self.assertTrue(all(row['time_s'] > 0 for row in rows))
            self.assertAlmostEqual(sum(row['time_s'] for row in rows), expected, places=6)


if __name__ == '__main__':
    unittest.main()

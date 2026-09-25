import gzip
import json
import math
from pathlib import Path
from types import SimpleNamespace
import unittest
from analyze_run import parse
from mapped_controller import Driver
import torcs_jm_par as entry

ROOT = Path(__file__).resolve().parent


class MappedTests(unittest.TestCase):
    def test_backward_envelope_is_brake_feasible(self):
        driver = Driver(json.loads((ROOT/'best_params.json').read_text()))
        for i, speed in enumerate(driver.envelope):
            self.assertLessEqual(speed**2, driver.envelope[(i+1)%driver.n]**2+
                                 2*driver.p['braking_accel']*driver.ds+1e-9)

    def test_periodic_lookup(self):
        driver = Driver()
        for distance in [-10, 0, 400, 1000]:
            self.assertAlmostEqual(driver.lookup(driver.envelope, distance),
                                   driver.lookup(driver.envelope,distance+driver.model['length_m']))

    def test_bad_parameters_fail_explicitly(self):
        with self.assertRaises(ValueError):
            Driver({'braking_accel': 0})
        with self.assertRaises(ValueError):
            Driver({'typo': 1})

    def test_default_entry_replays_every_recorded_command(self):
        # Verifies the public default adapter, not just the experimental harness.
        run=ROOT/'experiments/20260924T175352_782702Z_mapped-v2'
        client=SimpleNamespace(S=SimpleNamespace(d={}), R=entry.DriverAction())
        with gzip.open(run/'packets.jsonl.gz','rt') as source:
            for line in source:
                record=json.loads(line)
                client.S.d=parse(record['sensor'])
                entry.drive_mapped_v2_r1(client)
                action=parse(repr(client.R))
                expected=parse(record['action'])
                for key in ['steer','accel','brake','gear','clutch','meta']:
                    self.assertTrue(math.isfinite(action[key]))
                    self.assertEqual(action[key],expected[key],(record['step'],key))


if __name__ == '__main__':
    unittest.main()

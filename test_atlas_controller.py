import json
from pathlib import Path
import unittest
from atlas_controller import Driver
from experimental_controller import Driver as Reference
from lap_delta import load

ROOT=Path(__file__).resolve().parent


class AtlasTests(unittest.TestCase):
    def test_disabled_launch_preserves_controller_actions(self):
        params=json.loads((ROOT/'candidate_v3_params.json').read_text())
        left,right=Driver(params),Reference(params)
        for row in load(ROOT/'experiments/20260924T182501_227244Z_experimental-v3'):
            self.assertEqual(left.step(row['s']),right.step(row['s']))

    def test_launch_does_not_retrigger_on_new_lap(self):
        rows=load(ROOT/'experiments/20260924T182501_227244Z_experimental-v3')
        driver=Driver(dict(launch_clutch=.7,launch_duration=2,launch_rpm=5000))
        s=dict(rows[0]['s'],curLapTime=.02,distRaced=3618,speedX=2)
        self.assertEqual(driver.step(s)['clutch'],0)

    def test_launch_tracks_simulation_time(self):
        s=load(ROOT/'experiments/20260924T182501_227244Z_experimental-v3')[0]['s']
        driver=Driver(dict(launch_clutch=.8,launch_duration=2))
        for t,expected in [(-.5,.8),(0,.8),(1,.4),(2,0)]:
            self.assertAlmostEqual(driver.step(dict(s,curLapTime=t))['clutch'],expected)


if __name__=='__main__':unittest.main()

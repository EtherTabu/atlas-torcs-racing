"""Conservative sensor-only candidate; parameters are controller settings only."""
import math


def clamp(value, low, high):
    return max(low, min(high, value))


class Driver:
    VERSION = 'geometry-v1'

    def __init__(self):
        self.gear = 1
        self.shift_wait = 0
        self.steer = 0.0

    def step(self, s):
        speed = s['speedX']
        v = max(0, speed / 3.6)
        track = s['track']
        # Forward free distance is a visibility constraint, not an assertion
        # that a ray endpoint is the road centerline or curvature measurement.
        visible = max(0, track[9])
        target = min(70.0, max(30.0, 3.6 * math.sqrt(2 * 3.0 * max(0, visible - 12))))
        target = min(target, 70.0 / (1 + 2 * abs(s['angle'])))
        if abs(s['trackPos']) > .55:
            target = min(target, 40.0)
        desired = 3.0 * s['angle'] - .45 * s['trackPos'] - .015 * s['speedY']
        self.steer += clamp(desired - self.steer, -.06, .06)
        self.steer = clamp(self.steer, -1, 1)
        error = target - speed
        brake = clamp(-error * .08, 0, .65) if error < -1 else 0.0
        accel = clamp(.25 + error * .12, 0, 1) if not brake else 0.0
        wheels = s.get('wheelSpinVel', [0, 0, 0, 0])
        if len(wheels) == 4:
            front = (wheels[0] + wheels[1]) / 2
            rear = (wheels[2] + wheels[3]) / 2
            if speed > 5 and rear - front > 3:
                accel *= .5
            if v > 5 and front * .33 < v * .8:
                brake *= .4
        # Distinct up/down thresholds and a minimum dwell prevent hunting.
        self.shift_wait = max(0, self.shift_wait - .02)
        if self.shift_wait == 0:
            rpm = s['rpm']
            if rpm > 7500 and self.gear < 6:
                self.gear += 1
                self.shift_wait = .7
            elif rpm < 3300 and self.gear > 1:
                self.gear -= 1
                self.shift_wait = .7
        return dict(steer=self.steer, accel=accel, brake=brake,
                    gear=self.gear, clutch=0, meta=0)

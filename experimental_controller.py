"""Telemetry-learned curvature preview with physical speed/braking envelopes."""
import json
import math
from pathlib import Path
from racing_controller import clamp

DEFAULTS = dict(lateral_accel=5.0, braking_accel=4.0, max_speed=170,
                heading_gain=3.0, position_gain=.5, lateral_damping=.015,
                feedforward=8.0, understeer=.0, preview_m=3.0,
                speed_preview_m=8.0, steer_rate=3.0, brake_gain=.065,
                upshift_rpm=8000, downshift_rpm=3500, traction_slip=0, zones=[], local_controls=[],
                line_points=[], line_heading_gain=1.0, min_gear=1, braking_zones=[])


class Driver:
    VERSION = 'experimental-v3'

    def __init__(self, params=None):
        unknown = set(params or {}) - set(DEFAULTS)
        if unknown:
            raise ValueError('Unknown controller parameters: ' + ', '.join(sorted(unknown)))
        self.p = dict(DEFAULTS, **(params or {}))
        if any(self.p[k] <= 0 for k in ['lateral_accel', 'braking_accel', 'max_speed', 'steer_rate']):
            raise ValueError('Speed, acceleration and steering-rate limits must be positive')
        self.model = json.loads(Path(__file__).with_name('track_model.json').read_text())
        self.curvature = self.model['curvature']
        self.ds = self.model['spacing_m']
        self.n = len(self.curvature)
        p = self.p
        self.envelope = []
        for i, k in enumerate(self.curvature):
            lateral = p['lateral_accel']
            for start, end, cap in p['zones']:
                if start <= i*self.ds <= end:
                    lateral = min(lateral, cap)
            self.envelope.append(min(p['max_speed']/3.6, math.sqrt(lateral/max(abs(k), .0001))))
        # Periodic backwards braking propagation: every target is reachable
        # before the next local curvature limit with the declared deceleration.
        for _ in range(3):
            for i in range(self.n-1, -1, -1):
                decel = p['braking_accel']
                for start,end,value in p['braking_zones']:
                    if start<=i*self.ds<=end:
                        decel=value
                self.envelope[i] = min(self.envelope[i], math.sqrt(self.envelope[(i+1)%self.n]**2 + 2*decel*self.ds))
        self.steer = 0
        self.gear = 1
        self.shift_wait = 0
        self.last_time = None
        self.debug = {}

    def lookup(self, values, distance):
        cell = (distance % self.model['length_m']) / self.ds
        i = int(cell)
        f = cell-i
        return values[i%self.n]*(1-f) + values[(i+1)%self.n]*f

    def line(self, distance):
        points=self.p['line_points']
        for (a,ya),(b,yb) in zip(points,points[1:]):
            if a<=distance<=b:
                u=(distance-a)/(b-a)
                # Cubic smoothstep: continuous heading at all line knots.
                value=ya+(yb-ya)*u*u*(3-2*u)
                slope=(yb-ya)*6*u*(1-u)/(b-a)
                return value, math.atan(6*slope)
        return 0,0

    def step(self, s):
        p = self.p
        for start,end,overrides in self.p['local_controls']:
            if start <= s['distFromStart'] <= end:
                weight = min(1, (s['distFromStart']-start)/10, (end-s['distFromStart'])/10)
                p = dict(p)
                for key,value in overrides.items():
                    p[key] = p[key]+weight*(value-p[key])
        now = s['curLapTime']
        dt = clamp(now-self.last_time, .002, .1) if self.last_time is not None and now>self.last_time else .02
        self.last_time = now
        speed = s['speedX']
        v = max(0, speed/3.6)
        d = s['distFromStart']
        k = self.lookup(self.curvature, d+p['preview_m'])
        target = self.lookup(self.envelope, d+p['speed_preview_m'])*3.6
        line,line_heading=self.line(d)
        desired = ((p['feedforward']+p['understeer']*v*v)*k + p['heading_gain']*(s['angle']+p['line_heading_gain']*line_heading)
                   -p['position_gain']*(s['trackPos']-line)-p['lateral_damping']*s['speedY'])
        self.steer = clamp(self.steer+clamp(desired-self.steer, -p['steer_rate']*dt, p['steer_rate']*dt), -1, 1)
        error = target-speed
        brake = clamp(-error*p['brake_gain'], 0, .9) if error < -1 else 0
        accel = clamp(.25+error*.12, 0, 1) if not brake else 0
        wheels = s['wheelSpinVel']
        front, rear = sum(wheels[:2])/2, sum(wheels[2:])/2
        if p['traction_slip'] > 0 and speed > 5:
            slip = max(0, (rear*.3276 - front*.3306)/max(front*.3306, 5))
            accel *= clamp((2*p['traction_slip']-slip)/p['traction_slip'], .1, 1)
        elif speed>5 and rear-front>3:
            accel *= .5
        if v>5 and front*.33<v*.8:
            brake *= .4
        # Hold launch gear while the simulator counts down; use actual gear
        # engagement and simulated elapsed time rather than wall-time dwell.
        self.shift_wait = max(0, self.shift_wait-dt)
        if now <= 0 or speed < 5:
            self.gear = 1
        elif self.shift_wait == 0:
            if s['rpm']>p['upshift_rpm'] and self.gear<6:
                self.gear += 1
                self.shift_wait = .7
            elif s['rpm']<p['downshift_rpm'] and self.gear>p['min_gear']:
                self.gear -= 1
                self.shift_wait = .7
        self.debug = dict(target_speed=target, curvature=k, desired_steer=desired)
        return dict(steer=self.steer, accel=accel, brake=brake, gear=self.gear, clutch=0, meta=0)

"""ATLAS spatial control with an explicit, simulation-time standing-start launch."""
from experimental_controller import Driver as SpatialDriver
import math


class Driver(SpatialDriver):
    VERSION='atlas-v1-experimental'

    def __init__(self,params=None):
        params=dict(params or {})
        self.launch_clutch=params.pop('launch_clutch',0)
        self.launch_duration=params.pop('launch_duration',1)
        self.launch_rpm=params.pop('launch_rpm',0)
        self.launch_gain=params.pop('launch_gain',.0004)
        self.clutch_state=self.launch_clutch
        self.launch_previous=None
        self.velocity_heading_weight=params.pop('velocity_heading_weight',0)
        self.velocity_heading_regions=params.pop('velocity_heading_regions',[])
        self.steer_cap=params.pop('steer_cap',1)
        self.steer_cap_regions=params.pop('steer_cap_regions',[])
        if not 0<=self.launch_clutch<=1 or self.launch_duration<=0:
            raise ValueError('Invalid clutch launch settings')
        super().__init__(params)

    def step(self,s):
        control_state=s
        if self.velocity_heading_weight:
            d=s['distFromStart']
            weight=max([max(0,min(1,(d-a)/20,(b-d)/20)) for a,b in self.velocity_heading_regions],default=1)
            p=self.p
            for a,b,overrides in self.p['local_controls']:
                if a<=d<=b:
                    blend=min(1,(d-a)/10,(b-d)/10)
                    p=dict(p)
                    for key,value in overrides.items():p[key]+=blend*(value-p[key])
            correction=p['lateral_damping']*s['speedY']/p['heading_gain']-math.atan2(s['speedY'],max(s['speedX'],5))
            control_state=dict(s,angle=s['angle']+weight*self.velocity_heading_weight*correction)
        action=super().step(control_state)
        if self.steer_cap<1:
            d=s['distFromStart']
            weight=max([max(0,min(1,(d-a)/20,(b-d)/20)) for a,b in self.steer_cap_regions],default=1)
            cap=1-weight*(1-self.steer_cap)
            self.steer=max(-cap,min(cap,self.steer))
            action['steer']=self.steer
        # Only the first standing start, never a later lap or a recovery stop.
        if s['distRaced']<30 and s['speedX']<70:
            t=max(0,s['curLapTime'])
            action['clutch']=self.launch_clutch*max(0,1-t/self.launch_duration)
            if self.launch_rpm and t<self.launch_duration and s['speedX']<50:
                dt=max(0,min(.1,t-self.launch_previous)) if self.launch_previous is not None else 0
                self.clutch_state=max(0,min(.98,self.clutch_state+self.launch_gain*(self.launch_rpm-s['rpm'])*dt))
                action['clutch']=self.clutch_state
                self.gear=1
                action['gear']=1
                self.shift_wait=0
            self.launch_previous=t
        return action

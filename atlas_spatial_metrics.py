"""Spatial saturation and estimated body-clearance evidence, no validity relaxation."""
import json
import math
from pathlib import Path
import sys
from lap_delta import load


def report(run):
    rows=load(run);bins=[]
    for start in range(0,3600,100):
        group=[r for r in rows if start<=r['d']<start+100 and r['t']>=0]
        if not group:continue
        clearance=[6*(1-abs(r['s']['trackPos']))-
            .5*(1.94*abs(math.cos(r['s']['angle']))+4.52*abs(math.sin(r['s']['angle']))) for r in group]
        bins.append(dict(start_m=start,end_m=start+100,
            min_estimated_body_clearance_m=min(clearance),
            max_abs_trackPos=max(abs(r['s']['trackPos']) for r in group),
            max_abs_speedY_kmh=max(abs(r['s']['speedY']) for r in group),
            min_speed_kmh=min(r['s']['speedX'] for r in group),
            max_speed_kmh=max(r['s']['speedX'] for r in group),
            steering_saturation_fraction=sum(abs(r['a']['steer'])>=.999 for r in group)/len(group),
            braking_saturation_fraction=sum(r['a']['brake']>=.89 for r in group)/len(group)))
    result=dict(run=run.name,geometry=dict(track_width_m=12,body_length_m=4.52,body_width_m=1.94),
        note='Plan-view rectangle estimate from installed car dimensions; excludes roll/pitch and curved-boundary geometry. Does not replace the unchanged .6 trackPos gate.',bins=bins)
    (run/'spatial_limits.json').write_text(json.dumps(result,indent=2))
    return result


if __name__=='__main__':print(json.dumps(report(Path(sys.argv[1])),indent=2))

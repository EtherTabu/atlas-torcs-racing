"""Interpolated spatial lap deltas and control-event diagnostics, full packets."""
import bisect
import gzip
import json
from pathlib import Path
import sys
from analyze_run import parse

ROOT=Path(__file__).resolve().parent
REFERENCE=ROOT/'experiments/20260924T175529_575096Z_mapped-v2'
BOUNDARIES=[-10,300,600,950,1200,1800,2300,2600,2900,3150,3400,3608.4498865]


def load(run):
    rows=[]; offset=0; previous=None
    for line in gzip.open(run/'packets.jsonl.gz','rt'):
        r=json.loads(line);s=parse(r['sensor']);a=parse(r['action'])
        if previous is not None and s['curLapTime']<previous-.5:
            offset+=s['lastLapTime']
        rows.append(dict(d=s['distRaced']-10,t=s['curLapTime']+offset,s=s,a=a))
        previous=s['curLapTime']
    return rows


def segments(rows):
    # Remove stationary/reversing launch points for monotone interpolation.
    monotone=[]
    for r in rows:
        if not monotone or r['d']>monotone[-1]['d']:
            monotone.append(r)
    xs=[r['d'] for r in monotone]
    def at(d,key):
        if key=='t' and d==BOUNDARIES[0]: return 0
        if key=='t' and d==BOUNDARIES[-1] and rows[-1]['s']['lastLapTime']>0:
            return rows[-1]['s']['lastLapTime']
        i=max(1,min(len(xs)-1,bisect.bisect_left(xs,d)))
        a,b=monotone[i-1],monotone[i]
        av=a['t'] if key=='t' else a['s'][key]
        bv=b['t'] if key=='t' else b['s'][key]
        return av+(bv-av)*(d-a['d'])/(b['d']-a['d'])
    result=[]
    for start,end in zip(BOUNDARIES,BOUNDARIES[1:]):
        if xs[-1]<end-.5: break
        rr=[r for r in rows if start<=r['d']<=end and r['t']>=0]
        if not rr:continue
        braking=[r for r in rr if r['a']['brake']>.03]
        slow=min(rr,key=lambda r:r['s']['speedX'])
        pickup=next((r for r in rr if r['d']>=slow['d'] and r['a']['accel']>.5 and r['a']['brake']<.01),None)
        rates=[abs(b['a']['steer']-a['a']['steer'])/(b['t']-a['t']) for a,b in zip(rr,rr[1:]) if b['t']>a['t']]
        slip=[(sum(r['s']['wheelSpinVel'][2:])*.3276-sum(r['s']['wheelSpinVel'][:2])*.3306)/
              max(sum(r['s']['wheelSpinVel'][:2])*.3306,10) for r in rr]
        gears=[r['a']['gear'] for i,r in enumerate(rr) if i==0 or r['a']['gear']!=rr[i-1]['a']['gear']]
        result.append(dict(start_m=start,end_m=end,time_s=at(end,'t')-at(start,'t'),
            entry_speed=at(start,'speedX'),exit_speed=at(end,'speedX'),
            brake_onset_m=braking[0]['d'] if braking else None,
            brake_release_m=braking[-1]['d'] if braking else None,
            peak_brake=max(r['a']['brake'] for r in rr),min_speed=slow['s']['speedX'],
            min_speed_m=slow['d'],throttle_pickup_m=pickup['d'] if pickup else None,
            max_steer=max(abs(r['a']['steer']) for r in rr),max_steer_rate=max(rates,default=0),
            max_angle=max(abs(r['s']['angle']) for r in rr),
            min_trackPos=min(r['s']['trackPos'] for r in rr),max_trackPos=max(r['s']['trackPos'] for r in rr),
            max_speedY=max(abs(r['s']['speedY']) for r in rr),max_wheel_slip=max(slip),
            gears=gears,rpm_range=[min(r['s']['rpm'] for r in rr),max(r['s']['rpm'] for r in rr)],
            track_sensors_at_entry=rr[0]['s']['track'],track_sensors_at_min_speed=slow['s']['track'],
            track_sensors_at_exit=rr[-1]['s']['track']))
    return result


def report(run):
    data=segments(load(run)); reference=segments(load(REFERENCE))
    for row,ref in zip(data,reference):
        row['delta_s']=row['time_s']-ref['time_s']
    result=dict(run=run.name,reference=REFERENCE.name,segments=data)
    (run/'lap_delta.json').write_text(json.dumps(result,indent=2))
    return result


if __name__=='__main__':
    r=report(Path(sys.argv[1]))
    for s in r['segments']:
        print({k:round(v,3) if isinstance(v,float) else v for k,v in s.items() if not k.startswith('track_sensors')})

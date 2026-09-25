"""Learn road-heading curvature only from an identified clean telemetry lap."""
import bisect
import gzip
import json
import math
from pathlib import Path
from analyze_run import parse

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'experiments/20260924T172602_564431Z_geometry-v1'


def build():
    data = []
    with gzip.open(SOURCE / 'packets.jsonl.gz', 'rt') as source:
        for line in source:
            p = json.loads(line)
            s = parse(p['sensor'])
            data.append(s)
    # Both are emitted by this installed official SCR server: yaw is vehicle
    # orientation, angle is road tangent minus yaw. No track XML is consulted.
    length = data[0]['distFromStart'] + data[-1]['distRaced'] - data[-1]['distFromStart']
    # distRaced includes an extra circuit relative to the initial location.
    length /= 2
    samples = sorted((s['distFromStart'], s['yaw'] + s['angle']) for s in data if s['distRaced'] > 15)
    x, headings = [], []
    for distance, heading in samples:
        if x and distance <= x[-1]:
            continue
        if headings:
            heading = headings[-1] + (heading-headings[-1]+math.pi) % (2*math.pi)-math.pi
        x.append(distance)
        headings.append(heading)
    def heading_at(distance):
        i = max(1, min(len(x)-1, bisect.bisect_left(x, distance)))
        return headings[i-1] + (headings[i]-headings[i-1]) * (distance-x[i-1])/(x[i]-x[i-1])
    count = round(length/5)
    spacing = length/count
    curvature = []
    for i in range(count):
        d = i * spacing
        lo, hi = max(x[0], d-5), min(x[-1], d+5)
        curvature.append((heading_at(hi)-heading_at(lo))/(hi-lo))
    model = dict(version='telemetry-map-v1', source_run=SOURCE.name,
                 construction='road heading = server yaw + angle; spatial finite difference over 10 m',
                 runtime_sensors='distFromStart plus standard SCR feedback sensors; yaw only used offline',
                 length_m=length, spacing_m=spacing, curvature=curvature)
    (ROOT/'track_model.json').write_text(json.dumps(model, indent=2))
    print('Track length',length,'bins',count,'curvature range',min(curvature),max(curvature))
    print('Corner curvature by 100 m bins:')
    for d in range(0, int(length), 100):
        subset=curvature[int(d/spacing):int((d+100)/spacing)]
        print(d, round(max(subset,key=abs),4))


if __name__ == '__main__':
    build()

"""Rebuild simulation-rate telemetry and summarize complete packet evidence."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re


def parse(message):
    result = {}
    for key, values in re.findall(r'\((\w+)\s+([^()]*)\)', message):
        numbers = [float(x) for x in values.split()]
        result[key] = numbers[0] if len(numbers) == 1 else numbers
    return result


def analyze(run):
    from torcs_telemetry import Telemetry
    rows = []
    shifts = 0
    last_gear = None
    trajectory = hashlib.sha256()
    with gzip.open(run / 'packets.jsonl.gz', 'rt') as source:
        for line in source:
            packet = json.loads(line)
            sensor = parse(packet['sensor'])
            action = parse(packet['action'])
            trajectory.update((packet['sensor'] + '\n' + packet['action'] + '\n').encode())
            rows.append((packet, sensor, action))
            if last_gear is not None and action.get('gear') != last_gear:
                shifts += 1
            last_gear = action.get('gear')
    if not rows:
        return {}
    first, last = rows[0][1], rows[-1][1]
    result = dict(packets=len(rows), distance_m=last.get('distRaced'),
                  final_lap_time=last.get('curLapTime'), gear_command_changes=shifts,
                  damage_increase=max(s.get('damage', 0) for _, s, _ in rows)-first.get('damage', 0),
                  damage_present_all=all('damage' in s for _, s, _ in rows),
                  max_abs_trackPos=max(abs(s.get('trackPos', 0)) for _, s, _ in rows),
                  max_abs_angle=max(abs(s.get('angle', 0)) for _, s, _ in rows),
                  max_speed_kmh=max(s.get('speedX', 0) for _, s, _ in rows),
                  steering_saturation_packets=sum(abs(a.get('steer', 0)) >= .999 for _, _, a in rows),
                  brake_packets=sum(a.get('brake', 0) > 0 for _, _, a in rows),
                  standing_start_speed_kmh=first.get('speedX'),
                  trajectory_sha256=trajectory.hexdigest(),
                  note='No official validity flag supplied; trackPos is car-center position, not tire clearance.')
    summary = json.loads((run / 'summary.json').read_text())
    crossings = sum(b[1].get('distFromStart', 0) < a[1].get('distFromStart', 0) - 3000
                    for a, b in zip(rows, rows[1:]))
    checks = dict(
        completed=summary['reason'] == 'lap_complete_candidate' and crossings == 2
                  and last.get('lastLapTime', 0) > 0 and last.get('distRaced', 0) >= 3600,
        standing_start=abs(first.get('speedX', 999)) < .1 and first.get('distRaced', 999) == 0,
        no_damage=result['damage_present_all'] and result['damage_increase'] == 0 and first['damage'] == 0,
        conservative_track_margin=all(abs(s.get('trackPos', 999)) <= .6 for _, s, _ in rows),
        all_track_sensors_on_road=all(isinstance(s.get('track'), list) and len(s['track']) == 19
                                    and min(s['track']) >= 0 for _, s, _ in rows),
        contiguous_records=all(p['step'] == i for i, (p, _, _) in enumerate(rows, 1)),
        installed_assets_unchanged=summary.get('assets_unchanged') is True,
    )
    result['validity_checks'] = checks
    result['local_validity'] = 'passed' if all(checks.values()) else 'not_passed'
    result['lap_time_s'] = last.get('lastLapTime') if checks['completed'] else None
    # Full packet stream is authoritative. CSV is decimated to one in five
    # physics packets (~10 Hz simulation time), independent of wall-clock speed.
    with (run / 'simulation_telemetry.csv').open('w', newline='') as output:
        writer = csv.writer(output)
        writer.writerow(['step', 'wall_s'] + list(Telemetry.SENSOR_FIELDS) +
                        [x + '_cmd' for x in Telemetry.COMMAND_FIELDS] +
                        ['wheelSpinVel_' + str(i) for i in range(4)] +
                        ['track_' + str(i) for i in range(19)])
        for packet, s, a in rows[::5]:
            writer.writerow([packet['step'], packet['wall_s']] +
                            [s.get(k, '') for k in Telemetry.SENSOR_FIELDS] +
                            [a.get(k, '') for k in Telemetry.COMMAND_FIELDS] +
                            Telemetry._vector(s.get('wheelSpinVel'), 4) +
                            Telemetry._vector(s.get('track'), 19))
    (run / 'analysis.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print('Last 3 seconds (step, dist, speed, heading, trackPos, steer, throttle, brake):')
    for p, s, a in rows[-150::25]:
        print(p['step'], *(round(s.get(k, 0), 3) for k in ['distRaced', 'speedX', 'angle', 'trackPos']),
              *(a.get(k) for k in ['steer', 'accel', 'brake']))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    analyze(parser.parse_args().run)

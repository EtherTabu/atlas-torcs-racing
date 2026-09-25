"""Render standalone engineering figures from a preserved ATLAS packet trace."""
import argparse
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
from atlas_controller import Driver
from lap_delta import load, segments, REFERENCE

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', help='Project-relative preserved ATLAS run')
    args = parser.parse_args()
    run = (ROOT / args.run).resolve()
    if not run.is_relative_to(ROOT):
        raise ValueError('Evidence must be project-local')
    rows = load(run)
    manifest = json.loads((run / 'manifest.json').read_text())
    for name in ['atlas_controller.py', 'experimental_controller.py', 'track_model.json']:
        if manifest['source_sha256'][name] != hashlib.sha256((ROOT / name).read_bytes()).hexdigest():
            raise ValueError('Replay dependency differs from run: ' + name)
    driver = Driver(json.loads((run / 'parameters.json').read_text()))
    targets, lines = [], []
    for row in rows:
        driver.step(row['s'])
        targets.append(driver.debug['target_speed'])
        lines.append(driver.line(row['s']['distFromStart'])[0])
    active = [i for i, row in enumerate(rows) if row['t'] >= 0 and row['d'] >= 0]
    distance = [rows[i]['d'] for i in active]
    def sensor(key):
        return [rows[i]['s'][key] for i in active]
    def action(key):
        return [rows[i]['a'][key] for i in active]
    output = ROOT / 'artifacts' / run.name
    output.mkdir(parents=True, exist_ok=True)
    analysis = json.loads((run / 'analysis.json').read_text())
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, ax = plt.subplots(4, 1, figsize=(14, 10), sharex=True, constrained_layout=True)
    fig.suptitle('ATLAS | Corkscrew standing start | ' + str(analysis['lap_time_s']) + ' s\n'
                 'Recorded commands and sensors; target speed/line replayed from matching control sources', fontsize=15)
    ax[0].plot(distance, sensor('speedX'), label='Measured speed', color='#126a91')
    ax[0].plot(distance, [targets[i] for i in active], label='Planned target', color='#dc7f23', alpha=.85)
    ax[0].set_ylabel('Speed (km/h)')
    ax[0].legend(loc='lower left', ncol=2)
    ax[1].plot(distance, action('accel'), label='Throttle', color='#207d55')
    ax[1].plot(distance, action('brake'), label='Brake', color='#b63645')
    ax[1].set_ylabel('Command')
    ax[1].legend(loc='upper right', ncol=2)
    ax[2].plot(distance, sensor('trackPos'), label='Measured trackPos', color='#126a91')
    ax[2].plot(distance, [lines[i] for i in active], label='Line target', color='#dc7f23', alpha=.8)
    ax[2].axhline(.6, color='#b63645', linestyle=':', label='Local validity gate ±0.6')
    ax[2].axhline(-.6, color='#b63645', linestyle=':')
    ax[2].set_ylabel('Normalized offset')
    ax[2].legend(loc='upper right', ncol=3)
    ax[3].step(distance, sensor('gear'), label='Measured gear', color='#6d4a96')
    ax[3].set_ylabel('Gear')
    ax[3].set_xlabel('Distance beyond start/finish (m); initial 10 m standing-start approach excluded from plot')
    for axis in ax:
        axis.grid(alpha=.2)
    fig.savefig(output / 'controls.png', dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(14, 7), constrained_layout=True)
    points = np.array(list(zip(sensor('x'), sensor('y'))))
    collection = LineCollection(np.stack([points[:-1], points[1:]], axis=1), cmap='viridis', linewidth=3)
    collection.set_array(np.array(sensor('speedX')[:-1]))
    ax[0].add_collection(collection)
    ax[0].autoscale()
    ax[0].set_aspect('equal')
    ax[0].set_title('Recorded vehicle path — not road boundaries')
    ax[0].set_xlabel('World x (m)')
    ax[0].set_ylabel('World y (m)')
    fig.colorbar(collection, ax=ax[0], label='Measured speed (km/h)', shrink=.7)
    candidate, reference = segments(rows), segments(load(REFERENCE))
    labels = [str(int(s['start_m'])) + '–' + str(int(s['end_m'])) + ' m' for s in candidate]
    gains = [r['time_s'] - c['time_s'] for c, r in zip(candidate, reference)]
    ax[1].barh(labels, gains, color=['#207d55' if value >= 0 else '#b63645' for value in gains])
    ax[1].invert_yaxis()
    ax[1].set_xlabel('Seconds saved versus preserved 95.310 s reference')
    ax[1].set_title('Spatial time gains, including standing-start approach')
    ax[1].grid(axis='x', alpha=.2)
    fig.savefig(output / 'path_and_delta.png', dpi=150)
    plt.close(fig)
    (output / 'provenance.json').write_text(json.dumps(dict(run=run.name,
        trajectory_sha256=analysis['trajectory_sha256'], lap_time_s=analysis['lap_time_s'],
        reference=REFERENCE.name, local_validity=analysis['local_validity'],
        note='Figures do not independently establish timing or GUI qualification.'), indent=2))
    print(output)


if __name__ == '__main__':
    main()

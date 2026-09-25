"""Isolated Linux/Podman TORCS experiments. All output lives in this project."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time
from types import SimpleNamespace
import xml.etree.ElementTree as ET

import torcs_jm_par as legacy
from torcs_telemetry import Telemetry

ROOT = Path(__file__).resolve().parent
INSTALL = Path('/usr/local/torcs')
DATA = INSTALL / 'share/games/torcs'
LIB = INSTALL / 'lib/torcs'
ANGLES = [-45, -19, -12, -7, -4, -2.5, -1.7, -1, -.5, 0, .5, 1, 1.7, 2.5, 4, 7, 12, 19, 45]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assets():
    paths = []
    for relative in ('cars/car1-trb1', 'drivers/scr_server', 'tracks/road/corkscrew'):
        paths.extend(p for p in (DATA / relative).rglob('*') if p.is_file())
    paths.extend([LIB / 'torcs-bin', LIB / 'drivers/scr_server/scr_server.so',
                  LIB / 'modules/simu/simuv2.so', LIB / 'lib/libraceengine.so'])
    return {str(p): digest(p) for p in paths if p.exists()}


def prepare(run):
    local = run / 'torcs_local'
    # Windows bind mounts do not support Linux copystat/utime reliably.
    for path in (DATA / 'config').rglob('*'):
        target = local / 'config' / path.relative_to(DATA / 'config')
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
    (local / 'results').mkdir()
    # Copy, never edit the active GUI configuration or installed assets.
    original = Path('/home/student/.torcs/config/raceman/practice.xml')
    shutil.copyfile(original, run / 'practice_original.xml')
    tree = ET.parse(original)
    root = tree.getroot()
    def set_value(path, value):
        node = root.find(path)
        if node is None:
            raise RuntimeError('Missing race config field: ' + path)
        node.set('val', str(value))
    set_value("./section[@name='Tracks']/section[@name='1']/attstr[@name='name']", 'corkscrew')
    set_value("./section[@name='Tracks']/section[@name='1']/attstr[@name='category']", 'road')
    set_value("./section[@name='Drivers']/section[@name='1']/attstr[@name='module']", 'scr_server')
    set_value("./section[@name='Drivers']/section[@name='1']/attnum[@name='idx']", 0)
    set_value("./section[@name='Practice']/section[@name='Starting Grid']/attnum[@name='initial speed']", 0)
    set_value("./section[@name='Practice']/attnum[@name='laps']", 2)
    set_value("./section[@name='Practice']/attstr[@name='display mode']", 'results only')
    config = run / 'race.xml'
    tree.write(config, encoding='utf-8', xml_declaration=True)
    return local, config


def run_experiment(args):
    if not (LIB / 'torcs-bin').exists():
        raise SystemExit('Run inside the existing torcs container; see ENGINEERING.md.')
    # Never attach to or kill somebody else's running simulator.
    existing = subprocess.run(['pgrep', '-x', 'torcs-bin'], capture_output=True, text=True)
    if existing.returncode == 0:
        raise SystemExit('A TORCS process is already running; refusing an ambiguous run.')
    run = ROOT / 'experiments' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ') + '_' + args.controller)
    run.mkdir(parents=True)
    source = run / 'source'
    source.mkdir()
    for path in ROOT.glob('*.py'):
        shutil.copyfile(path, source / path.name)
    for path in ROOT.glob('*.json'):
        shutil.copyfile(path, source / path.name)
    param_name = args.params
    if param_name is None and args.controller == 'mapped-v2':
        param_name = 'best_params.json'
    param_path = (ROOT / param_name).resolve() if param_name else None
    if param_path is not None and not param_path.is_relative_to(ROOT):
        raise ValueError('Controller parameters must be inside this project')
    parameters = json.loads(param_path.read_text()) if param_path else {}
    (run / 'parameters.json').write_text(json.dumps(parameters, indent=2))
    before = assets()
    local, config = prepare(run)
    manifest = dict(run_id=run.name, controller=args.controller, arguments=vars(args),
                    source_sha256={p.name: digest(p) for p in source.iterdir()}, parameters=parameters,
                    assets_sha256=before, race_sha256=digest(config), angles=ANGLES,
                    target=dict(track='corkscrew', driver='scr_server 1', driver_index=0,
                                standing_start=True), status='starting')
    manifest_path = run / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2))
    command = [str(LIB / 'torcs-bin'), '-l', str(local) + '/', '-L', str(LIB),
               '-D', str(DATA), '-r', str(config)]
    manifest['simulator_command'] = command
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = str(LIB / 'lib')
    env['DISPLAY'] = ':1'
    client = SimpleNamespace(S=legacy.ServerState(), R=legacy.DriverAction())
    if args.controller == 'modular-steer8':
        drive = legacy.drive_modular
    elif args.controller == 'legacy-example':
        drive = legacy.drive_example
    elif args.controller == 'geometry-v1':
        drive = legacy.drive_geometry_v1
    elif args.controller == 'audit-collision':
        drive = lambda c: c.R.d.update(steer=0, accel=1, brake=0, gear=2, clutch=0, meta=0)
    else:
        if args.controller == 'experimental-v3':
            from experimental_controller import Driver
        else:
            from mapped_controller import Driver
        driver = Driver(parameters)
        drive = lambda c: c.R.d.update(driver.step(c.S.d))
    summary = dict(reason='not_started', packets=0, first=None, last=None,
                   max_abs_trackPos=0, max_abs_angle=0, max_damage=0,
                   lap_events=[], standing_start_observed=False)
    process = None
    started = time.monotonic()
    previous_lap_time = None
    initial_damage = None
    print('RUN ' + str(run), flush=True)
    try:
        with (run / 'simulator.log').open('w') as simlog, \
             gzip.open(run / 'packets.jsonl.gz', 'wt', compresslevel=1) as raw, \
             socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock, \
             Telemetry(args.controller, directory=run, live=False) as telemetry:
            process = subprocess.Popen(command, cwd=DATA, env=env, stdout=simlog, stderr=subprocess.STDOUT)
            sock.settimeout(1)
            server = ('127.0.0.1', 3001)
            init = ('SCR(init ' + ' '.join(map(str, ANGLES)) + ')').encode()
            while time.monotonic() - started < 30:
                if process.poll() is not None:
                    raise RuntimeError('Simulator exited; inspect simulator.log')
                sock.sendto(init, server)
                try:
                    message, _ = sock.recvfrom(2**17)
                except socket.timeout:
                    continue
                if b'***identified***' in message:
                    break
            else:
                raise TimeoutError('SCR handshake timed out')
            sock.settimeout(10)
            manifest['runtime_command'] = Path('/proc/' + str(process.pid) + '/cmdline').read_bytes().decode().split('\0')[:-1]
            mappings = Path('/proc/' + str(process.pid) + '/maps').read_text()
            (run / 'runtime_maps.txt').write_text(mappings)
            summary['reason'] = 'running'
            while True:
                message, _ = sock.recvfrom(2**17)
                packet = message.decode().rstrip('\0')
                if packet.startswith('***'):
                    summary['reason'] = packet
                    break
                # Fresh dictionary avoids silently reusing missing sensors.
                client.S.d.clear()
                client.S.parse_server_str(packet)
                s = client.S.d
                summary['packets'] += 1
                if summary['first'] is None:
                    summary['first'] = s.copy()
                    summary['standing_start_observed'] = abs(s.get('speedX', 999)) < 0.1
                    initial_damage = s.get('damage')
                summary['last'] = s.copy()
                summary['max_abs_trackPos'] = max(summary['max_abs_trackPos'], abs(s.get('trackPos', 0)))
                summary['max_abs_angle'] = max(summary['max_abs_angle'], abs(s.get('angle', 0)))
                summary['max_damage'] = max(summary['max_damage'], s.get('damage', 0))
                lap = s.get('curLapTime')
                if previous_lap_time is not None and lap is not None and lap < previous_lap_time - 0.5:
                    summary['lap_events'].append(dict(step=summary['packets'], lastLapTime=s.get('lastLapTime'),
                                                       distRaced=s.get('distRaced'), distFromStart=s.get('distFromStart')))
                previous_lap_time = lap
                drive(client)
                action = repr(client.R)
                if getattr(args, 'control_delay_ms', 0):
                    time.sleep(args.control_delay_ms / 1000)
                sock.sendto(action.encode(), server)
                telemetry.record(s, client.R.d, summary['packets'], client.S.servstr)
                raw.write(json.dumps(dict(step=summary['packets'], wall_s=time.monotonic()-started,
                                          sensor=packet, action=action), separators=(',', ':')) + '\n')
                if initial_damage is not None and s.get('damage', initial_damage) > initial_damage:
                    summary['reason'] = 'damage_increased'
                    break
                if abs(s.get('trackPos', 0)) > 1 and args.controller != 'audit-collision':
                    summary['reason'] = 'off_track'
                    break
                if summary['lap_events'] and s.get('distRaced', 0) > 1000:
                    summary['reason'] = 'lap_complete_candidate'
                    break
                if summary['packets'] >= args.max_steps:
                    summary['reason'] = 'step_limit'
                    break
    except BaseException as exc:
        summary['reason'] = type(exc).__name__ + ': ' + str(exc)
        raise
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        summary['wall_duration_s'] = time.monotonic() - started
        summary['assets_unchanged'] = assets() == before
        summary['validity'] = 'unverified'  # Analyst must examine complete evidence.
        (run / 'summary.json').write_text(json.dumps(summary, indent=2))
        manifest['status'] = summary['reason']
        manifest_path.write_text(json.dumps(manifest, indent=2))
        print(json.dumps({k: v for k, v in summary.items() if k not in ('first', 'last')}, indent=2), flush=True)
    return run


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--controller', choices=['modular-steer8', 'legacy-example', 'geometry-v1', 'mapped-v2', 'experimental-v3', 'audit-collision'], default='mapped-v2')
    parser.add_argument('--params', help='Project-relative JSON controller parameters')
    parser.add_argument('--max-steps', type=int, default=15000)
    parser.add_argument('--control-delay-ms', type=float, default=0, help='Wall-time robustness probe; does not change simulator timestep')
    run_experiment(parser.parse_args())

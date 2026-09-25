"""Real compile/test/integrity/timing/validity qualification; run inside TORCS container."""
import argparse
from datetime import datetime, timezone
import hashlib
import gzip
import itertools
import xml.etree.ElementTree as ET
import json
from pathlib import Path
import py_compile
import subprocess
import shutil
from qualify_timing import qualify
from race_experiment import assets, ROOT


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--params',default='atlas_params.json')
    parser.add_argument('--controller',choices=['atlas-v1','experimental-v3'],default='atlas-v1')
    parser.add_argument('--max-lap-time',type=float,default=85.0,help='Strict lap-time target for promotion')
    parser.add_argument('--repeats',type=int,default=3)
    parser.add_argument('--gui-run',help='Project-relative experiment directory of same frozen GUI candidate')
    parser.add_argument('--offline',action='store_true',help='Compile/tests only; never reports full qualification PASS')
    args=parser.parse_args()
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    output=ROOT/'qualification_reports'/stamp;output.mkdir(parents=True)
    report=dict(status='FAIL',controller=args.controller,checks={},runs=[])
    checks=report['checks']
    try:
        for path in ROOT.glob('*.py'):py_compile.compile(str(path),doraise=True)
        checks['compile']=True
        with (output/'unit_tests.log').open('w') as log:
            result=subprocess.run(['python3','-m','unittest','discover','-v'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        checks['unit_tests']=result.returncode==0
        if not checks['unit_tests']:raise RuntimeError('Unit tests failed')
        report['source_sha256']={p.name:digest(p) for p in ROOT.glob('*.py')}
        git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True) if shutil.which('git') else None
        report['git_commit']=git.stdout.strip() if git is not None and git.returncode==0 else None
        if args.offline:
            report['status']='OFFLINE_PASS_NOT_RACE_QUALIFIED'
        else:
            if args.repeats<2:raise ValueError('Qualification requires at least two repetitions per timing mode')
            params=(ROOT/args.params).resolve()
            if not params.is_relative_to(ROOT):raise ValueError('Parameters must be project-local')
            parameters=json.loads(params.read_text())
            report['parameter_sha256']=digest(params)
            report['map_sha256']=digest(ROOT/'track_model.json')
            before=assets();report['installed_assets_sha256']=before
            checks['assets_present']=len(before)>0
            reference=json.loads((ROOT/'experiments/20260924T175529_575096Z_mapped-v2/manifest.json').read_text())
            checks['reference_assets_match']=before==reference['assets_sha256']
            if not all(checks.values()):raise RuntimeError('Preflight integrity failed')
            rows=qualify(args.controller,str(params.relative_to(ROOT)),args.repeats)
            report['runs']=rows
            checks['all_locally_valid']=all(r['analysis']['local_validity']=='passed' for r in rows)
            checks['identical_trajectories']=len({r['analysis']['trajectory_sha256'] for r in rows})==1
            checks['performance_target_met']=all(r['analysis']['lap_time_s'] is not None and r['analysis']['lap_time_s']<args.max_lap_time for r in rows)
            report['strict_lap_target_s']=args.max_lap_time
            checks['parameters_match']=all(json.loads((ROOT/'experiments'/r['run']/'parameters.json').read_text())==parameters for r in rows)
            manifests=[json.loads((ROOT/'experiments'/r['run']/'manifest.json').read_text()) for r in rows]
            forbidden={'-nodamage','-nofuel','-nolaptime','-noisy'}
            checks['prohibited_flags_absent']=all(not forbidden.intersection(m['runtime_command']) for m in manifests)
            checks['live_telemetry_complete']=True
            checks['race_configuration_matches']=True
            for row,manifest in zip(rows,manifests):
                run=ROOT/'experiments'/row['run']
                summary=json.loads((run/'summary.json').read_text())
                checks['live_telemetry_complete'] &= summary.get('dropped_live_records')==0
                with gzip.open(run/'packets.jsonl.gz','rt') as left,gzip.open(run/'live/packets.jsonl.gz','rt') as right:
                    checks['live_telemetry_complete'] &= all(a==b for a,b in itertools.zip_longest(map(json.loads,left),map(json.loads,right)))
                config=ET.parse(run/'race.xml').getroot()
                expected={
                    "./section[@name='Tracks']/section[@name='1']/attstr[@name='name']":'corkscrew',
                    "./section[@name='Drivers']/section[@name='1']/attstr[@name='module']":'scr_server',
                    "./section[@name='Drivers']/section[@name='1']/attnum[@name='idx']":'0',
                    "./section[@name='Practice']/section[@name='Starting Grid']/attnum[@name='initial speed']":'0',
                }
                checks['race_configuration_matches'] &= all(config.find(path) is not None and config.find(path).get('val')==value for path,value in expected.items())
                checks['race_configuration_matches'] &= digest(run/'race.xml')==manifest['race_sha256']
            dependencies=['experimental_controller.py','racing_controller.py','torcs_jm_par.py','track_model.json']
            if args.controller=='atlas-v1':dependencies.append('atlas_controller.py')
            checks['run_control_sources_match']=all(all(m['source_sha256'][name]==digest(ROOT/name) for name in dependencies) for m in manifests)

            checks['assets_unchanged']=assets()==before
            checks['sources_unchanged']=all(digest(ROOT/name)==sha for name,sha in report['source_sha256'].items())
            report['lap_time_s']=rows[0]['analysis']['lap_time_s']
            report['confirmation_count']=len(rows)
            if args.gui_run:
                gui=(ROOT/args.gui_run).resolve()
                if not gui.is_relative_to(ROOT):raise ValueError('GUI evidence must be project-local')
                from analyze_run import analyze
                ga=analyze(gui);gm=json.loads((gui/'manifest.json').read_text())
                checks['gui_valid']=ga['local_validity']=='passed'
                checks['gui_same_trajectory']=ga['trajectory_sha256']==rows[0]['analysis']['trajectory_sha256']
                checks['gui_same_parameters']=gm['parameters']==parameters
                checks['gui_normal_mode']=gm['arguments'].get('gui',False) and '-r' not in gm['runtime_command']
                checks['gui_same_assets']=gm['assets_sha256']==before
                checks['gui_prohibited_flags_absent']=not forbidden.intersection(gm['runtime_command'])
                checks['gui_race_snapshot_hash']=digest(gui/'race.xml')==gm['race_sha256']
                # Runtime controller dependencies must match, not just the label.
                dependencies=['experimental_controller.py','racing_controller.py','torcs_jm_par.py','track_model.json']
                if args.controller=='atlas-v1':dependencies.append('atlas_controller.py')
                checks['gui_same_control_sources']=all(gm['source_sha256'][name]==digest(ROOT/name) for name in dependencies)
                report['gui_run']=gui.name
            report['status']=('PASS' if args.gui_run else 'TIMING_PASS_GUI_PENDING') if all(checks.values()) else 'FAIL'
    except Exception as exc:
        report['error']=str(exc)
    (output/'report.json').write_text(json.dumps(report,indent=2))
    print(report['status'],output/'report.json',flush=True)
    if report['status']=='FAIL':raise SystemExit(1)


if __name__=='__main__':main()

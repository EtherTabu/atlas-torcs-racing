"""Generate release identity from selected qualification; never run TORCS."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', default='evidence/qualified_checkpoint.json')
    parser.add_argument('--version', default='ATLAS RC1')
    parser.add_argument('--video', default=None)
    parser.add_argument('--manifest-only', action='store_true')
    args = parser.parse_args()
    path = (ROOT / args.checkpoint).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Checkpoint must be within the release tree')
    checkpoint = json.loads(path.read_text())
    report_path = ROOT / 'evidence/qualification.json'
    report = json.loads(report_path.read_text())
    if report['status'] != 'PASS' or not all(report['checks'].values()):
        raise ValueError('Selected evidence is not a full qualification PASS')
    if digest(report_path) != checkpoint['qualification_report_sha256']:
        raise ValueError('Qualification report differs from checkpoint')
    dependencies = ['atlas_controller.py', 'experimental_controller.py', 'racing_controller.py',
                    'mapped_controller.py', 'torcs_jm_par.py', 'competition_client.py',
                    'async_telemetry.py', 'torcs_telemetry.py', 'race_experiment.py']
    hashes = {name:digest(ROOT/name) for name in dependencies}
    if any(value != checkpoint['source_sha256'][name] for name,value in hashes.items()):
        raise ValueError('Packaged driving/runtime source differs from qualified candidate')
    for name,key in [('atlas_params.json','parameter_sha256'),('track_model.json','map_sha256')]:
        hashes[name] = digest(ROOT/name)
        if hashes[name] != checkpoint[key]:
            raise ValueError('Selected data hash differs: '+name)
    figures = json.loads((ROOT/'evidence/provenance.json').read_text())
    if figures['trajectory_sha256'] != checkpoint['analysis']['trajectory_sha256']:
        raise ValueError('Evidence plots belong to a different trajectory; regenerate them')
    livery = json.loads((ROOT/'assets/livery/provenance.json').read_text())
    if digest(ROOT/'assets/livery/car1-trb1.rgb') != livery['sha256']:
        raise ValueError('Livery changed')
    git = subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True) if shutil.which('git') else None
    commit = git.stdout.strip() if git is not None and git.returncode == 0 else None
    analysis = checkpoint['analysis']
    video_path = ROOT/'evidence/official_video.json'
    video = json.loads(video_path.read_text())
    if video['status'] != 'PASS' or video['analysis'] != analysis:
        raise ValueError('Recorded video evidence differs from qualified analysis')
    for name, expected in video['runtime_source_sha256'].items():
        if digest(ROOT/name) != expected:
            raise ValueError('Recorded runtime source differs: '+name)
    for actual, expected in [(digest(path), video['checkpoint_sha256']),
                             (digest(report_path), video['qualification_sha256']),
                             (livery['sha256'], video['livery_sha256'])]:
        if actual != expected:
            raise ValueError('Recorded qualification or livery identity differs')
    candidate = video['submission_candidate']
    if (not video['installed_assets_match_checkpoint'] or not video['race_matches_qualified_gui']
            or candidate['playback_speed'] != 1 or candidate['finish_hold_added']
            or candidate['max_relative_timestamp_deviation_ticks'] != 0):
        raise ValueError('Video consistency gate failed')
    manifest = dict(version=args.version,source_commit=commit,source_hashes=hashes,
        evidence_checkpoint_sha256=digest(path),qualification_sha256=digest(report_path),
        official_lap_time_s=analysis['lap_time_s'],trajectory_sha256=analysis['trajectory_sha256'],
        track='Corkscrew',driver='scr_server 1',standing_start=checkpoint['standing_start'],
        damage=analysis['damage_increase'],max_abs_trackPos=analysis['max_abs_trackPos'],
        peak_speed_kmh=analysis['max_speed_kmh'],timing_repetitions=report['confirmation_count'],
        gui_run=checkpoint['gui_run'],livery=livery,video=args.video or candidate['filename'],
        capture_source_commit=video['capture_source_commit'],official_video=video,
        official_video_evidence_sha256=digest(video_path),
        submission_ready=False,pending=video['pending'],
        provenance_note='Historical qualification binds byte-identical runtime sources by hash. The source commit is the packaging revision, not a claim about when the historical run occurred.')
    (ROOT/'dist').mkdir(exist_ok=True)
    (ROOT/'dist/submission_manifest.json').write_text(json.dumps(manifest,indent=2))
    if not args.manifest_only:
        table='| Checkpoint | Official lap (s) | Evidence level |\n|---|---:|---|\n'
        for name,time,level in [('Telemetry baseline',252.856,'Audited historical'),('Mapped reference',95.310,'Repeated reference'),('Spatial candidate',89.394,'Timing + GUI'),(args.version,analysis['lap_time_s'],'Timing + GUI')]:
            table+=f'| {name} | {time:.3f} | {level} |\n'
        hash_table='| Artifact | SHA-256 |\n|---|---|\n'+''.join(f'| `{name}` | `{sha}` |\n' for name,sha in hashes.items() if name in ['atlas_controller.py','atlas_params.json','track_model.json'])
        values=dict(BENCHMARK_TABLE=table,VERSION=args.version,LAP_TIME=f"{analysis['lap_time_s']:.3f}",REPEATS=str(report['confirmation_count']),PEAK_SPEED=f"{analysis['max_speed_kmh']:.3f}",TRACK_POS=f"{analysis['max_abs_trackPos']:.6f}",HASH_TABLE=hash_table,VIDEO=args.video or 'pending, not submission complete')
        values['VIDEO'] = args.video or candidate['filename']
        content=(ROOT/'README.template.md').read_text()
        for key,value in values.items():content=content.replace('{{'+key+'}}',value)
        if '{{' in content:raise ValueError('Unresolved README field')
        # Keep generated Markdown stable across Windows and Linux checkouts.
        with (ROOT/'README.md').open('w', encoding='utf-8', newline='\n') as output:
            output.write(content)
    print('Generated manifest; commit:',commit or 'not committed','submission_ready: false')


if __name__ == '__main__':
    main()

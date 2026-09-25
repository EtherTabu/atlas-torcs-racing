"""Matched reference/candidate timing suite grounded in the measured GUI run."""
import contextlib
import json
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime, timezone
from timing_experiment import run_experiment
from analyze_run import analyze
from analyze_timing import analyze as analyze_timing

GUI_TRACE = 'experiments/20260924T190741_134214Z_experimental-v3/packets.jsonl.gz'


def qualify(controller, params, repeats=3):
    result = []
    for kind in ['ordinary', 'fixed3ms', 'gui_resampled']:
        for seed in range(1, repeats+1):
            args = SimpleNamespace(controller=controller, params=params, max_steps=20000,
                buffer_logging=True, async_logging=True, control_delay_ms=3 if kind=='fixed3ms' else 0,
                delay_trace=GUI_TRACE if kind=='gui_resampled' else None, delay_seed=seed)
            # Empirical delays are ADDED to measured compute/transport time,
            # conservatively covering the observed 2.521 ms response maximum.
            with open(Path('campaigns')/'qualification_latest.log','a') as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                run = run_experiment(args)
                analysis = analyze(run)
                timing = analyze_timing(run)
            row = dict(kind=kind, seed=seed, run=run.name, analysis=analysis, timing=timing)
            result.append(row)
            print(controller, kind, seed, analysis['lap_time_s'], analysis['local_validity'], flush=True)
            stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
            (Path('campaigns')/('qualification_'+stamp+'.json')).write_text(json.dumps(result,indent=2))
    return result


if __name__ == '__main__':
    results = qualify('mapped-v2', 'best_params.json', 2)
    results += qualify('experimental-v3', 'candidate_v3_params.json', 3)
    Path('audit/timing_qualification.json').write_text(json.dumps(results,indent=2))

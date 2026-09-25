"""Client timing distributions and optional server deadline observations."""
import gzip
import json
from pathlib import Path
import statistics
import sys
from analyze_run import parse


def distribution(values):
    values = sorted(values)
    if not values:
        return None
    def quantile(q):
        x = q * (len(values) - 1)
        i = int(x)
        return values[i] + (values[min(i+1, len(values)-1)] - values[i]) * (x-i)
    return dict(n=len(values), mean=statistics.mean(values), median=quantile(.5),
                p95=quantile(.95), p99=quantile(.99), maximum=values[-1],
                jitter_stddev=statistics.pstdev(values))


def analyze(run):
    rows = [json.loads(x) for x in gzip.open(run/'packets.jsonl.gz', 'rt')]
    result = dict(run=run.name, units='milliseconds',
        response_latency=distribution([(r['sent_s']-r['received_s'])*1000 for r in rows]),
        receive_interval=distribution([(b['received_s']-a['received_s'])*1000 for a,b in zip(rows, rows[1:])]),
        send_interval=distribution([(b['sent_s']-a['sent_s'])*1000 for a,b in zip(rows, rows[1:])]))
    states = [parse(r['sensor']) for r in rows]
    result['simulation_interval'] = distribution([(b['curLapTime']-a['curLapTime'])*1000
        for a,b in zip(states, states[1:]) if b['curLapTime'] > a['curLapTime']])
    server = run/'server_select.csv'
    if server.exists():
        import csv
        events = list(csv.reader(server.open()))
        waits = [r for r in events if r[0] != 'R']
        result['server_wait'] = distribution([(float(r[2])-float(r[1]))*1000 for r in waits])
        result['timeouts'] = [r for r in waits if r[4]=='0']
        result['active_timeouts'] = [r for r in waits if r[4]=='0' and float(r[2])<=rows[-1]['sent_s']]
        result['shutdown_timeouts'] = [r for r in waits if r[4]=='0' and float(r[2])>rows[-1]['sent_s']]
    (run/'timing_analysis.json').write_text(json.dumps(result,indent=2))
    return result


if __name__ == '__main__':
    print(json.dumps(analyze(Path(sys.argv[1])),indent=2))

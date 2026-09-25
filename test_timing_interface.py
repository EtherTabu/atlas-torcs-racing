import gzip
import json
from pathlib import Path
import tempfile
import unittest
import ast
import inspect
from async_telemetry import AsyncTelemetry
from analyze_timing import distribution


class TimingInterfaceTests(unittest.TestCase):
    def test_worker_flushes_ordered_packets_on_shutdown(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            logger=AsyncTelemetry(directory,'test',live=False)
            for step in range(100):
                logger.record(dict(step=step,sensor='(speedX 1)',action='(accel 0)'),{'speedX':1},{'accel':0})
            logger.close()
            with gzip.open(Path(directory)/'packets.jsonl.gz','rt') as source:
                self.assertEqual([json.loads(line)['step'] for line in source],list(range(100)))
            self.assertEqual(logger.dropped,0)

    def test_harness_has_no_snapshot_io_after_handshake(self):
        import timing_experiment
        source=inspect.getsource(timing_experiment.run_experiment)
        active=source.split("if b'***identified***' in message:",1)[1].split('    finally:',1)[0]
        for forbidden in ('read_bytes(', 'read_text(', 'write_text('):
            self.assertNotIn(forbidden,active)

    def test_percentiles_and_jitter(self):
        d=distribution([1,2,3,4,5])
        self.assertEqual(d['median'],3)
        self.assertAlmostEqual(d['p95'],4.8)
        self.assertAlmostEqual(d['jitter_stddev'],2**.5)

    def test_response_loop_has_no_disk_or_console_calls(self):
        import competition_client
        tree=ast.parse(inspect.getsource(competition_client.main))
        loops=[n for n in ast.walk(tree) if isinstance(n,ast.While)]
        packet_loop=next(n for n in loops if any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute)
            and x.func.attr=='step' for x in ast.walk(n)))
        forbidden={'open','write','write_text','print','flush','dumps','sleep'}
        names={n.func.attr if isinstance(n.func,ast.Attribute) else n.func.id
               for n in ast.walk(packet_loop) if isinstance(n,ast.Call) and isinstance(n.func,(ast.Attribute,ast.Name))}
        self.assertFalse(names & forbidden)
        self.assertIn('record',names)
        self.assertIn('put_nowait',inspect.getsource(AsyncTelemetry.record))


if __name__=='__main__':unittest.main()

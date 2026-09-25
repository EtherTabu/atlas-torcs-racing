"""Offline checks; never connects to or launches TORCS."""

import csv
import io
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import torcs_jm_par as controller
from torcs_telemetry import Telemetry


class TelemetryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.addCleanup(self.temp.cleanup)
        self.output = io.StringIO()

    def logger(self, **kwargs):
        return Telemetry('test', directory=self.temp.name, stream=self.output, **kwargs)

    @staticmethod
    def rows(path):
        with path.open(newline='', encoding='utf-8') as source:
            return list(csv.DictReader(source))

    def test_rates_columns_commands_and_final_flush(self):
        now = [0.0]
        sensors = dict(speedX=72.0, speedY=-2.0, gear=3, damage=0,
                       wheelSpinVel=[1, 2, 3, 4], track=list(range(19)))
        action = controller.DriverAction()
        action.d.update(steer=1.5, accel=1.2, brake=-0.1, gear=4)
        repr(action)  # Same clipping/serialization as respond_to_server.
        with self.logger(clock=lambda: now[0]) as log:
            handle = log.file
            for step in range(100):  # Two seconds of 50 Hz sensor packets.
                now[0] = step / 50
                log.record(sensors, action.d, step + 1)
        self.assertTrue(handle.closed)
        rows = self.rows(log.path)
        self.assertEqual(len(rows), 20)
        self.assertEqual(len(self.output.getvalue().splitlines()), 11)  # Path + 10 statuses.
        self.assertEqual(rows[0]['elapsed_s'], '0.000000')
        self.assertEqual(rows[-1]['elapsed_s'], '1.900000')
        self.assertEqual(rows[0]['gear'], '3')
        self.assertEqual(rows[0]['gear_cmd'], '4.000')
        self.assertEqual(rows[0]['steer_cmd'], '1.000')
        self.assertEqual(rows[0]['brake_cmd'], '0.000')
        self.assertEqual(rows[0]['wheelSpinVel_3'], '4')
        self.assertEqual([rows[0]['track_' + str(i)] for i in range(19)],
                         [str(i) for i in range(19)])

    def test_missing_short_and_stale_fields(self):
        sensors = dict(speedX=10, damage=99, track=[5], wheelSpinVel=None)
        with self.logger() as log:
            log.record(sensors, {}, 1, '(speedX 10)(track 5)')
        row = self.rows(log.path)[0]
        for key in ('damage', 'rpm', 'track_1', 'track_18', 'wheelSpinVel_0', 'steer_cmd'):
            self.assertEqual(row[key], '')
        self.assertEqual(row['track_0'], '5')
        self.assertEqual(sensors['damage'], 99)  # No mutation of driver state.
        self.assertIn('rpm=?', self.output.getvalue())

    def test_no_catchup_burst_after_pause(self):
        now = [0.0]
        with self.logger(clock=lambda: now[0]) as log:
            log.record({}, {}, 1)
            now[0] = 10.0
            for step in range(2, 20):
                log.record({}, {}, step)
        self.assertEqual(len(self.rows(log.path)), 2)

    def test_disk_error_disables_csv_without_stopping_status(self):
        with self.logger() as log:
            handle = log.file
            with patch.object(log, 'writer') as writer:
                writer.writerow.side_effect = OSError('synthetic disk full')
                log.record({}, {}, 1)
            self.assertIsNone(log.file)
            self.assertTrue(handle.closed)
        self.assertIn('CSV disabled', self.output.getvalue())
        self.assertIn('rpm=?', self.output.getvalue())

    def test_runner_cleanup_on_shutdown_limit_interrupt_and_exception(self):
        for ending in ('shutdown', 'limit', 'interrupt', 'error'):
            with self.subTest(ending=ending):
                client = SimpleNamespace(maxSteps=3 if ending != 'limit' else 1,
                                         debug=False, so=True,
                                         S=SimpleNamespace(d={}, servstr=''),
                                         R=SimpleNamespace(d={}))
                calls = []
                logs = []

                def receive():
                    if calls:
                        if ending == 'interrupt':
                            raise KeyboardInterrupt
                        if ending == 'error':
                            raise RuntimeError('synthetic controller failure')
                        client.so = None

                def shutdown():
                    client.so = None

                def factory(name, live):
                    log = self.logger(live=live)
                    logs.append((log, log.file))
                    return log

                client.get_servers_input = receive
                client.respond_to_server = lambda: calls.append('send')
                client.shutdown = shutdown
                with patch.object(controller, 'Client', return_value=client), \
                     patch.object(controller, 'Telemetry', side_effect=factory):
                    if ending == 'interrupt':
                        with self.assertRaises(SystemExit) as result:
                            controller.run_controller(lambda c: None)
                        self.assertEqual(result.exception.code, 130)
                    elif ending == 'error':
                        with self.assertRaises(RuntimeError):
                            controller.run_controller(lambda c: None)
                    else:
                        controller.run_controller(lambda c: None)
                self.assertIsNone(client.so)
                self.assertEqual(calls, ['send'])
                self.assertTrue(logs[0][1].closed)
                self.assertEqual(len(self.rows(logs[0][0].path)), 1)


if __name__ == '__main__':
    unittest.main()

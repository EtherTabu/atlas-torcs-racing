"""Buffered, wall-clock-rate-limited telemetry; no changes to driver state."""

import csv
from datetime import datetime
from pathlib import Path
import sys
import time


class Telemetry:
    SENSOR_FIELDS = (
        'distRaced', 'distFromStart', 'speedX', 'speedY', 'rpm', 'gear',
        'angle', 'trackPos', 'damage', 'curLapTime', 'lastLapTime',
    )
    COMMAND_FIELDS = ('steer', 'accel', 'brake', 'gear')
    HEADER = (
        ('elapsed_s', 'step', 'controller') + SENSOR_FIELDS
        + tuple(name + '_cmd' for name in COMMAND_FIELDS)
        + tuple('wheelSpinVel_' + str(i) for i in range(4))
        + tuple('track_' + str(i) for i in range(19))
    )

    def __init__(self, controller, live=True, directory=None, clock=None, stream=None):
        self.controller = controller
        self.clock = clock or time.monotonic
        self.stream = stream if stream is not None else sys.stderr
        self.live = live
        self.tty = self.stream.isatty()
        self.started = None
        self.csv_slot = self.status_slot = self.flush_slot = -1
        self.file = None
        self.path = None
        self.status_width = 0
        directory = Path(directory) if directory is not None else Path(__file__).resolve().parent / 'telemetry'
        try:
            directory.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            self.path = directory / ('telemetry_' + stamp + '_' + controller + '.csv')
            self.file = self.path.open('x', newline='', encoding='utf-8', buffering=65536)
            self.writer = csv.writer(self.file)
            self.writer.writerow(self.HEADER)
            self.file.flush()
        except OSError as exc:
            self._csv_error(exc)
        if self.file is not None:
            self._output('Telemetry CSV: ' + str(self.path) + '\n')

    def _output(self, text):
        try:
            self.stream.write(text)
            self.stream.flush()
        except (OSError, ValueError):
            # A closed console/pipe must not interrupt driving or CSV logging.
            self.live = False

    def _csv_error(self, exc):
        self._output('\nTelemetry CSV disabled: ' + str(exc) + '\n')
        if self.file is not None:
            try:
                self.file.close()
            except OSError:
                pass
            self.file = None

    @staticmethod
    def _vector(value, size):
        if not isinstance(value, (list, tuple)):
            value = ()
        return [value[i] if i < len(value) else '' for i in range(size)]

    @staticmethod
    def _number(value, digits=2):
        if not isinstance(value, (int, float)):
            return '?'
        return format(value, '.' + str(digits) + 'f')

    def record(self, sensors, commands, step, server_string=None):
        now = self.clock()
        if self.started is None:
            self.started = now
        elapsed = now - self.started
        csv_slot = int(elapsed * 10 + 1e-9)
        status_slot = int(elapsed * 5 + 1e-9)
        write_csv = self.file is not None and csv_slot > self.csv_slot
        write_status = self.live and status_slot > self.status_slot
        if not (write_csv or write_status):
            return

        # The legacy parser retains old fields. Filter only at sample time so
        # a field absent from this packet is blank, never stale, in telemetry.
        if server_string is not None:
            present = {part.split(' ', 1)[0] for part in
                       server_string.strip().strip('()').split(')(')}
            sensors = {key: value for key, value in sensors.items() if key in present}

        if write_csv:
            self.csv_slot = csv_slot
            row = [format(elapsed, '.6f'), step, self.controller]
            row.extend(sensors.get(key, '') for key in self.SENSOR_FIELDS)
            # respond_to_server already clipped commands; match its 3 decimals.
            row.extend(self._number(commands.get(key), 3) if key in commands else ''
                       for key in self.COMMAND_FIELDS)
            row.extend(self._vector(sensors.get('wheelSpinVel'), 4))
            row.extend(self._vector(sensors.get('track'), 19))
            try:
                self.writer.writerow(row)
                if int(elapsed) > self.flush_slot:
                    self.file.flush()
                    self.flush_slot = int(elapsed)
            except OSError as exc:
                self._csv_error(exc)

        if write_status:
            self.status_slot = status_slot
            n = self._number
            line = (f'{self.controller} t={elapsed:6.1f}s '
                    f'd={n(sensors.get("distRaced"), 1)}m '
                    f'v={n(sensors.get("speedX"), 1)}km/h '
                    f'g={n(sensors.get("gear"), 0)}>{n(commands.get("gear"), 0)} '
                    f'rpm={n(sensors.get("rpm"), 0)} '
                    f'S/A/B={n(commands.get("steer"))}/{n(commands.get("accel"))}/{n(commands.get("brake"))} '
                    f'ang={n(sensors.get("angle"))} pos={n(sensors.get("trackPos"))}')
            if self.tty:
                self.status_width = max(self.status_width, len(line))
                self._output('\r' + line.ljust(self.status_width))
            else:
                self._output(line + '\n')

    def close(self):
        if self.file is not None:
            try:
                self.file.close()  # Flushes buffered CSV before closing.
            except OSError as exc:
                self._csv_error(exc)
            finally:
                self.file = None
        if self.status_width:
            self._output('\n')
            self.status_width = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()

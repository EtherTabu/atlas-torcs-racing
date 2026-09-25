"""Separate-process telemetry so disk/console stalls cannot hold the SCR loop."""
import gzip
import json
import multiprocessing as mp
from pathlib import Path
import queue
import signal
from torcs_telemetry import Telemetry


def _writer(messages, ready, directory, controller, live):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        with Telemetry(controller, directory=directory, live=live) as telemetry, gzip.open(
                Path(directory)/'packets.jsonl.gz', 'wt', compresslevel=1) as raw:
            while True:
                item = messages.get()
                if item == ():
                    ready.set()
                    continue
                if item is None:
                    break
                record, sensors, commands = item
                raw.write(json.dumps(record,separators=(',', ':'))+'\n')
                telemetry.record(sensors,commands,record['step'])
    finally:
        ready.set()


class AsyncTelemetry:
    def __init__(self, directory, controller, live=True):
        ctx = mp.get_context('spawn')
        self.messages = ctx.Queue(maxsize=4096)
        ready = ctx.Event()
        self.process = ctx.Process(target=_writer, args=(self.messages,ready,str(directory),controller,live))
        self.process.start()
        # Start the queue feeder and complete a writer round trip before SCR.
        self.messages.put_nowait(())
        if not ready.wait(30) or not self.process.is_alive():
            raise RuntimeError('Telemetry worker could not start before SCR connection')
        self.dropped = 0

    def record(self, record, sensors, commands):
        if not self.process.is_alive():
            self.dropped += 1
            return
        try:
            self.messages.put_nowait((record,sensors.copy(),commands.copy()))
        except queue.Full:
            self.dropped += 1

    def close(self):
        # Only shutdown can block; no commands depend on file/console progress.
        try:
            if self.process.is_alive():
                self.messages.put(None, timeout=30)
                self.process.join(30)
            if self.process.is_alive():
                raise RuntimeError('Telemetry writer did not close within 30 seconds')
            if self.process.exitcode:
                raise RuntimeError('Telemetry writer failed with exit code '+str(self.process.exitcode))
        except (queue.Full, RuntimeError):
            if self.process.is_alive():
                self.process.terminate()
                self.process.join(5)
            self.messages.cancel_join_thread()
            self.messages.close()
            raise
        self.messages.close()
        self.messages.join_thread()

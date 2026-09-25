"""Attach a preloaded spatial candidate to normal GUI SCR; never launches TORCS."""
import argparse
from datetime import datetime, timezone
import hashlib
import gc
import json
from pathlib import Path
import socket
import time
from async_telemetry import AsyncTelemetry
from atlas_controller import Driver
from torcs_jm_par import ServerState, DriverAction
from race_experiment import ANGLES

ROOT = Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--params',default='atlas_params.json')
    parser.add_argument('--host',default='localhost')
    parser.add_argument('--port',type=int,default=3001)
    parser.add_argument('--quiet',action='store_true')
    args=parser.parse_args()
    params=(ROOT/args.params).resolve()
    if not params.is_relative_to(ROOT): raise ValueError('Parameters must be project-local')
    # All loading, worker startup and directory creation precede handshake.
    parameters=json.loads(params.read_text())
    driver=Driver(parameters)
    output=ROOT/'telemetry'/datetime.now(timezone.utc).strftime('gui_%Y%m%dT%H%M%S_%fZ')
    output.mkdir(parents=True)
    manifest=dict(controller=Driver.VERSION,parameters=parameters,parameter_sha256=hashlib.sha256(params.read_bytes()).hexdigest(),source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        for name in ['competition_client.py','async_telemetry.py','atlas_controller.py','experimental_controller.py','racing_controller.py','torcs_jm_par.py','torcs_telemetry.py','race_experiment.py','track_model.json']})
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2))
    telemetry=AsyncTelemetry(output,Driver.VERSION,live=not args.quiet)
    state,action=ServerState(),DriverAction()
    server=(args.host,args.port)
    step=0; started=time.monotonic()
    gc_was_enabled=gc.isenabled()
    gc.collect()
    gc.disable()
    try:
        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
            sock.settimeout(1)
            while True:
                sock.sendto(('SCR(init '+' '.join(map(str,ANGLES))+')').encode(),server)
                try: message,_=sock.recvfrom(2**17)
                except socket.timeout: continue
                if b'***identified***' in message: break
            sock.settimeout(10)
            while True:
                data,_=sock.recvfrom(2**17)
                received=time.monotonic()
                packet=data.decode().rstrip('\0')
                if packet.startswith('***'):break
                state.d.clear();state.parse_server_str(packet)
                action.d.update(driver.step(state.d))
                command=repr(action)
                sock.sendto(command.encode(),server)
                sent=time.monotonic();step+=1
                telemetry.record(dict(step=step,received_s=received,sent_s=sent,
                    wall_s=sent-started,sensor=packet,action=command),state.d,action.d)
    except KeyboardInterrupt:
        pass
    finally:
        if gc_was_enabled:gc.enable()
        try:
            telemetry.close()
        finally:
            (output/'client_summary.json').write_text(json.dumps(dict(packets=step,dropped_records=telemetry.dropped),indent=2))
        print('Telemetry saved:',output,'dropped records:',telemetry.dropped)


if __name__=='__main__':main()

"""Low-speed ID 11 test. Physical support and clearance must be checked first."""
import argparse
import time
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dynamixel_bus import DynamixelBus


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', default='COM3')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    bus = DynamixelBus(args.port)
    enabled = False

    def read(id_, address, size):
        return bus.read(id_, address, size)

    def write(address, size, value):
        bus.write(11, address, size, value)

    def check():
        position = read(11, 132, 4)
        if read(11, 70, 1) or abs(position - start) > 55:
            raise RuntimeError('Hardware error or position outside test envelope')
        return position

    def move(target):
        write(116, 4, target)
        deadline, stable = time.monotonic() + 5, 0
        while time.monotonic() < deadline:
            position = check()
            stable = stable + 1 if abs(position - target) <= 5 else 0
            if stable >= 3:
                print(f'Reached {position} (target {target})')
                return
            time.sleep(0.1)
        raise RuntimeError('Target not reached: inspect support, load and cables before retrying')

    try:
        bus.open()
        if bus.ping(11) != 1020:
            raise RuntimeError('Expected XM430-W350 on ID 11')
        for id_ in range(11, 16):
            if read(id_, 64, 1) or read(id_, 70, 1):
                raise RuntimeError(f'ID {id_}: expected torque OFF and no errors')
        if read(11, 11, 1) != 3 or read(11, 10, 1) != 0 or read(11, 20, 4) != 0:
            raise RuntimeError('Unexpected base configuration')
        start = read(11, 132, 4)
        target = start + 34
        lower, upper = read(11, 52, 4), read(11, 48, 4)
        if not max(lower, 60) <= start <= target <= min(upper, 4035):
            raise RuntimeError('Outside configured limits or near single-turn boundary')
        print(f'ID 11: {start} -> {target} -> {start}, displacement=2.99 degrees')
        if not args.execute:
            print('Read-only preview: no registers written.')
            return
        # Mode 3: Goal PWM caps output; Goal Current is not a current limit here.
        write(100, 2, min(100, read(11, 36, 2)))
        write(108, 4, 1)
        write(112, 4, 3)
        write(116, 4, start)
        enabled = True
        write(64, 1, 1)
        move(target)
        print('Holding for 2 seconds')
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            check()
            time.sleep(0.1)
        move(start)
        print('Base movement and return verified.')
    finally:
        if bus.is_open:
            try:
                if enabled:
                    write(64, 1, 0)
                    print('Base torque disabled; low-output RAM settings retained.')
            finally:
                bus.close()


if __name__ == '__main__':
    main()

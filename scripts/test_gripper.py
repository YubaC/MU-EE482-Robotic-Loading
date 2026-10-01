"""Small, current-limited gripper test; other joints receive no writes."""
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
    parser.add_argument('--delta', type=int, default=20, help='Positive displacement, 1 to 80 counts')
    parser.add_argument('--hold', type=float, default=2.0, help='Hold at target, 0 to 3 seconds')
    args = parser.parse_args()
    if not 1 <= args.delta <= 80 or not 0 <= args.hold <= 3:
        parser.error('delta must be 1..80 and hold must be 0..3')
    bus = DynamixelBus(args.port)
    enabled = False

    def read(address, size):
        return bus.read(15, address, size)

    def write(address, size, value):
        bus.write(15, address, size, value)

    def move(target):
        write(116, 4, target)
        deadline = time.monotonic() + 4
        stable = 0
        while time.monotonic() < deadline:
            position = read(132, 4)
            if read(70, 1):
                raise RuntimeError('Hardware error')
            if abs(position - start) > args.delta + 20:
                raise RuntimeError('Position moved outside test envelope')
            stable = stable + 1 if abs(position - target) <= 5 else 0
            if stable >= 3:
                print(f'Reached {position} (target {target})')
                return
            time.sleep(0.1)
        raise RuntimeError('Target not reached; do not increase current without checking mechanism')

    try:
        bus.open()
        if bus.ping(15) != 1020:
            raise RuntimeError('Expected XM430-W350 on ID 15')
        if read(11, 1) != 5 or read(10, 1) != 0 or read(20, 4) != 0:
            raise RuntimeError('Unexpected operating mode, drive mode, or offset')
        if read(64, 1) or read(70, 1):
            raise RuntimeError('Expected torque OFF and no hardware error')
        start = read(132, 4)
        # Conservative test window around the standard gripper centre, not a
        # replacement for calibrating the actual mechanism's physical limits.
        if not 1750 <= start <= 2350 or start + args.delta > 2350:
            raise RuntimeError('Position outside conservative gripper test window')
        print(f'ID 15: start={start}; target={start + args.delta}; displacement={args.delta * 360 / 4096:.2f} motor degrees')
        if not args.execute:
            print('Read-only preview. Add --execute for the physical test.')
            return
        # RAM only: low current and nonzero velocity/acceleration profiles.
        write(102, 2, min(50, read(38, 2)))
        write(108, 4, 1)
        write(112, 4, 5)
        write(116, 4, start)
        enabled = True  # cleanup also runs if enable response is lost
        write(64, 1, 1)
        move(start + args.delta)
        print(f'Holding for {args.hold:.1f} seconds')
        deadline = time.monotonic() + args.hold
        while time.monotonic() < deadline:
            if read(70, 1) or abs(read(132, 4) - start) > args.delta + 20:
                raise RuntimeError('Unexpected state during hold')
            time.sleep(0.1)
        move(start)
        print('Small movement and return verified.')
    finally:
        if bus.is_open:
            try:
                if enabled:
                    write(64, 1, 0)
                    print('Gripper torque disabled; low-current RAM settings retained.')
            finally:
                bus.close()


if __name__ == '__main__':
    main()

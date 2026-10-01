"""Read-only Protocol 2.0 probe. Never writes registers or enables torque."""
import argparse
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dynamixel_bus import DynamixelBus, CommunicationError, DeviceError
from serial.tools import list_ports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port')
    parser.add_argument('--baud', type=int, default=1000000)
    parser.add_argument('--ids', type=int, nargs='+', default=list(range(11, 16)))
    args = parser.parse_args()
    if not args.port:
        for p in list_ports.comports():
            print(f'{p.device}: {p.description} [{p.hwid}]')
        return 0
    if any(i < 0 or i > 252 for i in args.ids):
        parser.error('IDs must be between 0 and 252')
    bus = DynamixelBus(args.port, args.baud)
    found = 0
    try:
        bus.open()
        for i in args.ids:
            try:
                model = bus.ping(i)
            except (CommunicationError, DeviceError) as exc:
                print(exc)
                continue
            found += 1
            print(f'ID {i}: model={model}')
            if model != 1020:
                print('  Unexpected model: skipping XM430-W350 register reads')
                continue
            for name, address, size in [('torque', 64, 1), ('hardware_error', 70, 1), ('position_raw', 132, 4), ('voltage_0.1V', 144, 2), ('temperature_C', 146, 1)]:
                try:
                    value = bus.read(i, address, size, signed=name == 'position_raw')
                except (CommunicationError, DeviceError) as exc:
                    print(f'  {name}: {exc}')
                else:
                    print(f'  {name}={value}')
        return 0 if found == len(args.ids) else 1
    except Exception as exc:
        print(f'Probe failed: {exc}', file=sys.stderr)
        return 2
    finally:
        bus.close()


if __name__ == '__main__':
    sys.exit(main())

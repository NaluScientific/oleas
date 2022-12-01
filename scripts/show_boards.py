"""Script to show connected FTDI devices"""

import sys

from naludaq.tools.ftdi import list_ftdi_devices




def main():
    try:
        devices = list_ftdi_devices(valid_only=True, bytes_to_str=True)
    except Exception:
        print('Cannot show devices. Is FTDI installed?')
        sys.exit(1)

    if len(devices) == 0:
        print('No devices found')
    else:
        msg = f'Found {len(devices)} device{"" if len(devices) == 1 else "s"}'
        print(msg)
        print('-' * len(msg))

    for index, device_dict in devices.items():
        print(f'Device {index}')
        print(f'    Serial Number: {device_dict["serial"]}')
        print(f'    Description: {device_dict["description"]}')


if __name__ == '__main__':
    main()

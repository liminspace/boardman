from typing import List, Optional, Tuple

import click
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo

from .constants import DEVICES
from .tools import device_details_to_print, match_device


@click.command()
def detect() -> Optional[Tuple[str, ListPortInfo]]:
    detected_devices: List[Tuple[str, ListPortInfo]] = []
    devices: List[ListPortInfo] = comports()
    for device in devices:
        detected_devices.extend(
            (possible_device_name, device)
            for possible_device_name, possible_device_data_items in DEVICES.items()
            if any(match_device(device=device, data=data) for data in possible_device_data_items)
        )
    if not detected_devices:
        click.echo("❌ No devices detected", err=True)
        raise click.Abort()

    if len(detected_devices) > 1:
        devices_details = [
            device_details_to_print(known_name=known_name, device=device)
            for known_name, device in detected_devices
        ]
        nl = "\n"
        click.echo(f"❌ Found more than one device:\n{nl.join(devices_details)}", err=True)
        raise click.Abort()

    known_name, device = detected_devices[0]
    device_details = device_details_to_print(known_name=known_name, device=device)
    click.echo(f"✅ Found device:\n{device_details}")

    return known_name, device

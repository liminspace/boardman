import hashlib
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from serial.tools.list_ports_common import ListPortInfo


def match_patterns(pattern: str, path: Path) -> bool:
    return (
        ("*" in pattern and path.match(pattern))
        or (pattern.endswith("/") and str(path).startswith(pattern))
        or (pattern == str(path))
    )


def get_base_path(config: Dict) -> Path:
    base_path = config["base_path"]
    if base_path is None:
        base_path = Path.cwd()
    base_path = Path(base_path).resolve(strict=True)
    return base_path


def device_details_to_print(known_name: str, device: ListPortInfo) -> str:
    return "\n".join(
        [
            f"🔌 [{known_name}] {device.device}",
            f"        Manufacturer: {device.manufacturer}",
            f"        Product: {device.product}",
            f"        Description: {device.description}",
            f"        HWID: {device.hwid}",
            f"        Location: {device.location}",
            f"        Interface: {device.interface}",
        ]
    )


def match_device(device: ListPortInfo, data: Dict[str, Any]) -> bool:
    if "hwid" in data and data["hwid"] not in device.whid:
        return False
    elif "manufacturer" in data and data["manufacturer"] != device.manufacturer:
        return False
    return True


def exec_cli(args: List[str], stdin: Optional[bytes] = None) -> bytes:
    cmd = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd_stdout, cmd_stderr = cmd.communicate(input=stdin)
    if cmd.returncode != 0:
        click.echo(
            (
                f"❌ Error on executing command: {' '.join(args)}\n"
                f"        return code: {cmd.returncode}\n"
                f"        stdout:\n{cmd_stdout.decode()}\n"
                f"        stderr:\n{cmd_stderr.decode()}\n"
            ),
            err=True,
        )
        raise click.Abort()

    return cmd_stdout


def board_get_file_content(
    dev_port: str,
    file_path: Path,
) -> bytes:
    return exec_cli(["ampy", "--port", dev_port, "get", str(file_path)])


def get_file_hash(file_path: Path) -> str:
    return hashlib.sha256(file_path.read_bytes()).hexdigest()

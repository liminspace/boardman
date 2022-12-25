import io
import os
import shutil
import subprocess
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

import click
import requests

from .constants import MICROPYTHON_URL_TPL


@click.command()
@click.option(
    "--ver",
    required=True,
    default="1.19.1",
    type=str,
    help="Version of MicroPython",
    show_default=True,
)
@click.option(
    "--path",
    required=True,
    default="mpy-cross",
    type=str,
    help="Path of executable file",
    show_default=True,
)
@click.pass_context
def get_mpy_compiler(ctx: click.Context, ver: str, path: str) -> None:
    with TemporaryDirectory(prefix="boardman_get_mpy_compiler_") as tmp_dir_path:
        url = MICROPYTHON_URL_TPL.format(ver=ver)

        click.echo(f"📦Download the file {url} ...")
        r = requests.get(url, allow_redirects=True)
        if r.status_code != 200:
            click.echo(f"❌ Bad response ({r.status_code} {r.reason})")
            raise click.Abort()
        click.echo(f"✅ OK. Got the file {len(r.content)} bytes")

        archive_bytes = io.BytesIO(r.content)
        del r

        click.echo("Extracting the archive...")
        with zipfile.ZipFile(archive_bytes, "r") as z:
            z.extractall(tmp_dir_path)
            click.echo("✅ OK")

        del archive_bytes

        dirs = [d for d in os.listdir(tmp_dir_path) if d.endswith(ver)]
        if len(dirs) != 1:
            click.echo(f"❌ Bad archive: expected 1 directory in archive, found {len(dirs)}")
            raise click.Abort()

        click.echo("🚀Build...")
        p = subprocess.Popen(
            ["make"],
            cwd=Path(tmp_dir_path) / dirs[0] / "mpy-cross",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if p.returncode != 0:
            print(out.decode())
            print(err.decode())
            click.echo(f"❌ Failed with status code {p.returncode}")
            raise click.Abort()
        click.echo("✅ OK")

        click.echo("➡️Copy the built file...")
        shutil.copy(
            Path(tmp_dir_path) / dirs[0] / "mpy-cross" / "mpy-cross",
            path,
        )
        click.echo(f"✅ OK: {Path(path).absolute()}")

        click.echo("🧹Clean...")

    click.echo("✅ Done.")

import shutil
import sys
from pathlib import Path

import click

from .config import get_config
from .tools import get_base_path, match_patterns


@click.command()
@click.pass_context
def collect(ctx: click.Context) -> None:
    config = get_config(config_path=ctx.obj["config_path"])

    base_path = get_base_path(config=config)

    src_path = base_path / Path(config["collector"]["source_path"])
    if not src_path.is_dir():
        click.echo(f"directory not found: {src_path}", err=True)
        sys.exit(1)

    click.echo(f"📂Source path: {src_path}")

    dist_path = base_path / Path(config["collector"]["dist_path"])
    click.echo(f"📂Dist path: {dist_path}")

    if dist_path.exists():
        click.echo("ℹ️Dist path is already exists. 🗑 Removing...")
        shutil.rmtree(dist_path)
        click.echo("✅ OK")

    dist_path.mkdir(parents=True, exist_ok=True)
    click.echo("✅ Created dist directory")

    ignore_patterns = [f"{(src_path / p)}/" for p in config["collector"]["ignore"] if p.endswith("/")]
    ignore_patterns.extend(
        [f"{(src_path / p)}" for p in config["collector"]["ignore"] if not p.endswith("/")]
    )
    ignore_patterns.append(str(src_path / config["on_board"]["meta_file_path"]))

    created_dirs = set()
    click.echo("ℹ️Copy files into dist dir...")
    for found_file_path in src_path.glob("**/*"):
        if not found_file_path.is_file():
            continue

        is_ignored = False
        for ignore_pattern in ignore_patterns:
            if match_patterns(pattern=ignore_pattern, path=found_file_path):
                click.echo(f"    🟡ignore: {found_file_path.relative_to(src_path)}")
                is_ignored = True
                break

        if is_ignored:
            continue

        found_file_rel_path = found_file_path.relative_to(src_path)
        found_file_dist_path = dist_path / found_file_rel_path
        found_file_dist_path_dir = found_file_dist_path.parent
        if found_file_dist_path_dir not in created_dirs:
            if not found_file_dist_path_dir.exists():
                found_file_dist_path_dir.mkdir(parents=True, exist_ok=True)
            created_dirs.add(found_file_dist_path_dir)

        click.echo(f"    🟢copy: {found_file_rel_path}")
        shutil.copy(found_file_path, found_file_dist_path)

    click.echo("✅ done.")

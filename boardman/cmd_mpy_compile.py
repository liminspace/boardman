from pathlib import Path

import click

from .config import get_config
from .tools import exec_cli, get_base_path, match_patterns


@click.command()
@click.pass_context
def mpy_compile(ctx: click.Context) -> None:
    config = get_config(config_path=ctx.obj["config_path"])
    include_rules = config["mpy_compiler"]["include"]
    exclude_rules = config["mpy_compiler"]["exclude"]
    remove_sources = config["mpy_compiler"]["remove_sources"]

    base_cmd = [config["mpy_compiler"]["cli_path"]]
    if config["mpy_compiler"]["optimization_level"] > 0:
        base_cmd.append(f"-{'O' * config['mpy_compiler']['optimization_level']}")

    base_cmd.extend(
        [
            f"-march={config['mpy_compiler']['arch']}",
            f"-msmall-int-bits={config['mpy_compiler']['small_int_bits']}",
            "-X",
            f"emit={config['mpy_compiler']['emit']}",
            "-X",
            f"heapsize={config['mpy_compiler']['heapsize']}",
        ]
    )

    base_path = get_base_path(config=config)

    dist_path = base_path / Path(config["collector"]["dist_path"])
    click.echo(f"📂Dist path: {dist_path}")

    click.echo(f"ℹ️Removing source after compiling: {'Enabled' if remove_sources else 'Disabled'}")

    click.echo("🚀Compile py -> mpy...")
    for found_file_path in dist_path.glob("**/*"):
        if not found_file_path.is_file():
            continue

        if found_file_path.suffix != ".py":
            continue

        found_file_rel_path = found_file_path.relative_to(dist_path)

        if include_rules:
            is_included = any(
                match_patterns(pattern=pattern, path=found_file_rel_path) for pattern in include_rules
            )
            if not is_included:
                click.echo(f"    🟡ignore: {found_file_rel_path} [not included]")
                continue

        if exclude_rules:
            is_excluded = any(
                match_patterns(pattern=pattern, path=found_file_rel_path) for pattern in exclude_rules
            )
            if is_excluded:
                click.echo(f"    🟡ignore:  {found_file_rel_path} [excluded]")
                continue

        click.echo(f"    🟢compile: {found_file_rel_path}")
        exec_cli(base_cmd + [str(found_file_path)])

        if remove_sources:
            found_file_path.unlink()

    click.echo("✅ done.")

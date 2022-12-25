from typing import cast

import click

from .cmd_collect import collect
from .cmd_deploy import deploy
from .cmd_detect import detect
from .cmd_get_mpy_compiler import get_mpy_compiler
from .cmd_mpy_compile import mpy_compile
from .cmd_reset import reset_hard


@click.group()
@click.option(
    "-c",
    "--config",
    required=True,
    default="boardman.yaml",
    type=str,
    help="Config file",
    show_default=True,
)
@click.pass_context
def cli(ctx, config: str):
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config


cli.add_command(cast(click.Command, collect))
cli.add_command(cast(click.Command, mpy_compile))
cli.add_command(cast(click.Command, get_mpy_compiler))
cli.add_command(cast(click.Command, detect))
cli.add_command(cast(click.Command, deploy))
cli.add_command(cast(click.Command, reset_hard))

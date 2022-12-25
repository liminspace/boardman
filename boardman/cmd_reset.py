import click

from .tools import exec_cli


@click.command()
@click.pass_context
def reset_hard(ctx: click.Context) -> None:
    from .cmd_detect import detect

    try:
        dev_info = ctx.invoke(detect)[1]
    except click.Abort:
        click.echo("❌ Couldn't detect one device")
        raise
    dev_port = dev_info.device

    click.echo("🔄Hard reset...")
    exec_cli(["ampy", "--port", dev_port, "reset", "--hard"])

    click.echo("✅ done.")

import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List

import click

from .config import get_config
from .entities import MetaInfo
from .tools import board_get_file_content, exec_cli, get_base_path, get_file_hash, match_patterns


def _board_delete_files(
    dev_port: str,
    board_files_list: List[Path],
    dist_path: Path,
    delete_ignore_patterns: List[str],
) -> None:
    for file_path in board_files_list:
        file_rel_path = file_path.relative_to(os.sep)  # noqa

        dist_file_path = dist_path / file_rel_path
        if dist_file_path.exists():
            continue

        is_ignored = False
        for pattern in delete_ignore_patterns:
            if match_patterns(pattern=pattern, path=file_rel_path):
                click.echo(f"    🟡ignore: {file_path}")
                is_ignored = True
                break

        if is_ignored:
            continue

        click.echo(f"    🟢delete: {file_path}")
        exec_cli(["ampy", "--port", dev_port, "rm", str(file_path)])


def _board_upload_files(
    dev_port: str,
    dist_path: Path,
    meta: MetaInfo,
    meta_file_dev_path: Path,
) -> None:
    new_files_hashes: Dict[str, str] = {}
    created_dirs = {Path("."), Path("/")}
    for found_file_path in dist_path.glob("**/*"):
        if not found_file_path.is_file():
            continue

        file_dev_path = Path("/") / found_file_path.relative_to(dist_path)
        file_hash = get_file_hash(found_file_path)
        new_files_hashes[str(file_dev_path)] = file_hash

        if meta.get_hash_for_file(file_dev_path) == file_hash:
            click.echo(f"    🟡skip: {file_dev_path}")
            continue

        file_dev_path_dir = file_dev_path.parent
        if file_dev_path_dir not in created_dirs:
            click.echo(f"    🟢create dir {file_dev_path_dir}")
            exec_cli(["ampy", "--port", dev_port, "mkdir", "--exists-okay", str(file_dev_path_dir)])
            created_dirs.add(file_dev_path_dir)

        click.echo(f"    🟢put file {file_dev_path}")
        exec_cli(["ampy", "--port", dev_port, "put", str(found_file_path), str(file_dev_path)])

        meta.add_hash_for_file(file_dev_path, file_hash)

    click.echo(f"    🔵Put meta file {meta_file_dev_path}")
    meta.replace_files_hashes(new_files_hashes)
    with NamedTemporaryFile("w", encoding="utf-8") as tmp_file:
        tmp_file.write(meta.json(sort_keys=True, indent=2, ensure_ascii=False))
        tmp_file.flush()
        exec_cli(["ampy", "--port", dev_port, "put", tmp_file.name, str(meta_file_dev_path)])


@click.command()
@click.pass_context
def deploy(ctx: click.Context) -> None:
    config = get_config(config_path=ctx.obj["config_path"])

    # get device port

    from .cmd_detect import detect

    try:
        dev_info = ctx.invoke(detect)[1]
    except click.Abort:
        click.echo("❌ Couldn't detect one device")
        raise
    dev_port = dev_info.device

    # get fs tree from device

    files_list_raw = exec_cli(["ampy", "--port", dev_port, "ls", "--recursive", "/"])
    board_files_list = [Path(t) for t in files_list_raw.decode().strip().split(os.linesep)]  # noqa
    del files_list_raw

    # remove files which exist in board but not exist in dist
    #   (except on_board.delete_ignore and on_board.meta_file_path)

    delete_ignore_patterns = config["on_board"].get("ignore", None)
    if delete_ignore_patterns is None:
        delete_ignore_patterns = []
    delete_ignore_patterns.append(config["on_board"]["meta_file_path"])

    base_path = get_base_path(config=config)
    dist_path = base_path / Path(config["collector"]["dist_path"])

    click.echo("ℹ️Delete files from the board...")
    _board_delete_files(
        dev_port=dev_port,
        board_files_list=board_files_list,
        dist_path=dist_path,
        delete_ignore_patterns=delete_ignore_patterns,
    )

    # get meta file
    meta_file_dev_path = Path("/") / Path(config["on_board"]["meta_file_path"])
    if meta_file_dev_path in board_files_list:
        click.echo(f"ℹ️Read meta file `{meta_file_dev_path}` from the board...")
        meta_file_raw = board_get_file_content(
            dev_port=dev_port,
            file_path=Path(config["on_board"]["meta_file_path"]),
        )
        meta = MetaInfo.parse_raw(meta_file_raw)
        del meta_file_raw
    else:
        click.echo(f"ℹ️Meta file `{meta_file_dev_path}` not found on the board")
        meta = MetaInfo()

    # upload files dist -> board but only if no hashsum or hashsum is different

    click.echo("ℹ️Upload files to the board...")
    _board_upload_files(
        dev_port=dev_port,
        dist_path=dist_path,
        meta=meta,
        meta_file_dev_path=meta_file_dev_path,
    )

    click.echo("✅ done.")

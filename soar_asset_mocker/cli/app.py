import os
from pathlib import Path
from typing import Annotated

import pkg_resources
import rich
import typer

from .fetch import RecordingFetcher
from .injector import inject_app

cli_app = typer.Typer()


@cli_app.command()
def fetch(
    container_id: int,
    output_path: str,
    username: Annotated[str, typer.Option(prompt=True)],
    password: Annotated[str, typer.Option(prompt=True, hide_input=True)],
    phantom_url: str = os.getenv("PHANTOM_URL", ""),
    max_attachments: int = 500,
    verify_ssl: bool = False,
):
    if not phantom_url:
        phantom_url = typer.prompt("Enter SOAR url (or fill PHANTOM_URL env variable): ")
    RecordingFetcher(phantom_url, username, password, verify_ssl).fetch(
        container_id,
        output_path,
        max_attachments,
    )


@cli_app.command()
def inject(app_json_path: Path):  # pragma: no cover
    inject_app(app_json_path)


@cli_app.command()
def version():
    am_version = pkg_resources.get_distribution("soar_asset_mocker").version
    rich.print(f"SOAR Asset Mocker version: {am_version}")


if __name__ == "__main__":
    cli_app()

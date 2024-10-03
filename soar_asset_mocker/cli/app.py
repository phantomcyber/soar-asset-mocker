import os
from pathlib import Path
from typing import Annotated

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
        phantom_url = typer.prompt(
            "Enter SOAR url (or fill PHANTOM_URL env variable): "
        )
    RecordingFetcher.fetch(
        phantom_url,
        container_id,
        output_path,
        username,
        password,
        max_attachments,
        verify_ssl,
    )


@cli_app.command()
def inject(app_json_path: Path):  # pragma: no cover
    inject_app(app_json_path)


@cli_app.command()
def unpack(): ...


@cli_app.command()
def pack(): ...


if __name__ == "__main__":
    cli_app()

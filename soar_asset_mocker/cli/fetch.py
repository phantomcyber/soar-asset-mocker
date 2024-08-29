from typing import Any

import typer
import urllib3
import yaml
from requests import Session
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning

from soar_asset_mocker.utils.redactor import update_nested_dict

urllib3.disable_warnings()


class RecordingFetcher:

    @classmethod
    def fetch(
        cls,
        phantom_url: str,
        container_id: int,
        output_path: str,
        username: str,
        password: str,
        max_attachments: int = 50,
        verify_ssl: bool = False,
    ):
        fetcher = cls(phantom_url, username, password, verify_ssl)
        attachments = fetcher.get_attachments(container_id, max_attachments)
        if len(attachments) == 0:
            print("No attachments to preview, record some actions first")
            exit(2)
        first_index, last_index = fetcher.select_range()
        recording = fetcher.download_recordings(
            first_index, last_index, attachments
        )
        with open(output_path, "w") as f:
            yaml.dump(recording, f)
        print(f"Recording available at {output_path}")

    def __init__(
        self,
        phantom_url: str,
        username: str,
        password: str,
        verify_ssl: bool,
    ) -> None:
        self.s = self.get_session(username, password, verify_ssl)
        self.url = phantom_url

    def download_recording(self, attachment):
        resp = self.s.get(
            f"{self.url}/rest/vault_document/{attachment['vault_document']}"
        )
        doc = resp.json()

        resp = self.s.get(
            f"{self.url}/rest/download_attachment?vault_id={doc['hash']}"
        )
        return yaml.safe_load(resp.text)

    def download_recordings(
        self, first_index: int, last_index: int, attachments: list[dict]
    ):
        recordings: dict[Any, Any] = {}
        print("Dowloading")
        for i, attachment in enumerate(
            attachments[first_index : last_index + 1]
        ):
            print(i, attachment["name"])
            update_nested_dict(recordings, self.download_recording(attachment))
        return recordings

    @staticmethod
    def get_session(username: str, password: str, verify_ssl: bool = False):
        s = Session()
        s.auth = HTTPBasicAuth(username, password)
        if not verify_ssl:
            urllib3.disable_warnings(InsecureRequestWarning)
            s.verify = False
        return s

    @staticmethod
    def select_range():
        range_prompt = typer.prompt(
            "Select attachments range to download, such as 1-2"
        )
        range_split = range_prompt.split("-")
        start, stop = int(range_split[0]), int(range_split[1])
        return start, stop

    def get_attachments(self, container_id: int, max: int):
        print("Downloading Attachments")
        resp = self.s.get(
            f"{self.url}/rest/container/{container_id}/attachments?sort=create_time&order=desc&page=0&page_size=1000",
        )
        if resp.status_code != 200:
            print("Something went wrong:", resp.status_code, resp.text)
            exit(1)
        attachments = resp.json().get("data", [])
        attachments = attachments[: min(25, len(attachments))]
        for i, a in enumerate(attachments):
            print(f"{i} {a['name']}")
        return attachments

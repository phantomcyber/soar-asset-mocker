from collections import defaultdict
from typing import Any, Optional, Sequence

import msgpack
import typer
import urllib3
from requests import Session
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning

from soar_asset_mocker.utils.redactor import update_nested_dict

urllib3.disable_warnings()


class RecordingFetcher:

    def __init__(
        self,
        phantom_url: str,
        username: str,
        password: str,
        verify_ssl: bool,
    ) -> None:
        self.s = self.get_session(username, password, verify_ssl)
        self.url = phantom_url

    @classmethod
    def fetch(
        cls,
        phantom_url: str,
        container_id: int,
        output_path: str,
        username: str,
        password: str,
        max_attachments: int = 1000,
        verify_ssl: bool = False,
    ):
        fetcher = cls(phantom_url, username, password, verify_ssl)
        actions, playbooks = fetcher.get_attachments(
            container_id, max_attachments
        )
        if not actions and not playbooks:
            print("No attachments to preview, record some actions first")
            exit(2)
        recording: dict[Any, Any] = {}
        print(f"{len(actions)} actions found")
        if actions:
            fetcher.fetch_actions(actions, recording)
        print(f"{len(playbooks.keys())} playbooks found")
        if playbooks:
            fetcher.fetch_playbooks(playbooks, recording)
        with open(output_path, "wb") as f:
            msgpack.dump(recording, f)
        print(f"Recording available at {output_path}")

    def fetch_actions(self, actions: list[dict], recording: dict[Any, Any]):
        print()
        print("Showing catched actions")
        for i, attachment in enumerate(actions):
            meta = attachment["_pretty_metadata"]
            action_run_id = meta["action_run_id"] or 0
            print(
                f"\t* {i} {meta['app_name']} {meta.get('action_name','unknown_action')} run id:{action_run_id} {attachment['create_time']}"
            )
        print()
        indexes = self.select_indexes()
        print("Dowloading action recordings")
        recording = self.download_recordings(actions, recording, indexes)

    def fetch_playbooks(
        self, playbooks: defaultdict, recording: dict[Any, Any]
    ):
        print()
        print("Showing catched playbooks")
        pbids = list(playbooks.keys())
        for i, pbid in enumerate(pbids):
            print(
                f"\t* {i} {pbid} [{len(playbooks[pbid])} actions] {playbooks[pbid][0]['create_time']}"
            )
        print()
        pbindex = self.select_playbook()
        if pbindex is not None:
            print("Dowloading playbook recordings")
            recording = self.download_recordings(
                playbooks[pbids[pbindex]], recording
            )

    def download_recording(self, attachment):
        resp = self.s.get(
            f"{self.url}/rest/vault_document/{attachment['vault_document']}"
        )
        doc = resp.json()

        resp = self.s.get(
            f"{self.url}/rest/download_attachment?vault_id={doc['hash']}"
        )
        return msgpack.unpackb(resp.content)

    def download_recordings(
        self,
        attachments: list[dict],
        recording_pack: dict,
        indexes: Optional[Sequence[int]] = None,
    ):
        if not indexes:
            indexes = range(len(attachments))
        for i in indexes:
            print(i, attachments[i]["name"])
            update_nested_dict(
                recording_pack, self.download_recording(attachments[i])
            )

    @staticmethod
    def get_session(username: str, password: str, verify_ssl: bool = False):
        s = Session()
        s.auth = HTTPBasicAuth(username, password)
        if not verify_ssl:
            urllib3.disable_warnings(InsecureRequestWarning)
            s.verify = False
        return s

    @staticmethod
    def select_indexes():
        index_prompt = typer.prompt(
            "Select attachments to download, such as 1,2,3"
        )
        index_split = index_prompt.split(",")
        return [int(i) for i in index_split]

    @staticmethod
    def select_playbook():
        index_prompt = typer.prompt(
            "Select playbook to download, single number"
        )
        try:
            return int(index_prompt)
        except ValueError:
            return None

    def get_attachments(self, container_id: int, max: int):
        print("Downloading Attachments")
        resp = self.s.get(
            f"{self.url}/rest/container/{container_id}/attachments?sort=create_time&order=desc&page=0&page_size={max}&pretty=true",
        )
        if resp.status_code != 200:
            print("Something went wrong:", resp.status_code, resp.text)
            exit(1)
        attachments = resp.json().get("data", [])
        actions = []
        playbooks = defaultdict(lambda: [])
        for i, a in enumerate(attachments):
            metadata = a["_pretty_metadata"]
            if "scope" not in metadata:  # TODO Change to AM version
                continue
            pb_run_id = metadata.get("playbook_run_id")
            if pb_run_id:
                pb_name = metadata.get("playbook_name")
                app_name = metadata.get("app_name")
                playbooks[f"{app_name}_{pb_name}_{pb_run_id}"].append(a)
            else:
                actions.append(a)
        return actions, playbooks

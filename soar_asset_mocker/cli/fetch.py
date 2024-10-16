from collections import defaultdict
from typing import Optional, Sequence

import msgpack
import typer
import urllib3
from requests import Session
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning

from soar_asset_mocker.utils.redactor import update_nested_dict

urllib3.disable_warnings(InsecureRequestWarning)


class RecordingFetcher:

    def __init__(
        self,
        phantom_url: str,
        username: str,
        password: str,
        verify_ssl: bool = False,
    ) -> None:
        self.session = self.get_session(username, password, verify_ssl)
        self.url = phantom_url

    def fetch(
        self,
        container_id: int,
        output_path: str,
        max_attachments: int = 1000,
    ):
        actions, playbooks = self.get_attachments(container_id, max_attachments)
        if not actions and not playbooks:
            print("No attachments to preview, record some actions first")
            exit(2)
        recording: dict = {}
        print(f"{len(actions)} actions found")
        if actions:
            self.fetch_actions(actions, recording)
        print(f"{len(playbooks)} playbooks found")
        if playbooks:
            self.fetch_playbook(playbooks, recording)
        with open(output_path, "wb") as f:
            msgpack.dump(recording, f)
        print(f"Recording available at {output_path}")

    def fetch_actions(self, actions: list[dict], recording: dict):
        print("\nShowing caught actions")
        for i, attachment in enumerate(actions):
            meta = attachment["_pretty_metadata"]
            action_run_id = meta.get("action_run_id", 0)
            print(
                f"\t* {i} {meta['app_name']} {meta.get('action_name','unknown_action')} run id:{action_run_id} {attachment['create_time']}"
            )
        indexes = self.select_indexes()
        print("\nDownloading action recordings")
        recording = self.download_recordings(actions, recording, indexes)

    def fetch_playbook(self, playbooks: defaultdict, recording: dict):
        print("\nShowing caught playbooks")
        pbids = list(playbooks)
        for i, pbid in enumerate(pbids):
            print(f"\t* {i} {pbid} [{len(playbooks[pbid])} actions] {playbooks[pbid][0]['create_time']}")
        print()  # newline
        pbindex = self.select_playbook()
        if pbindex is not None:
            print("Downloading playbook recordings")
            recording = self.download_recordings(playbooks[pbids[pbindex]], recording)

    def download_recording(self, attachment):
        resp = self.session.get(f"{self.url}/rest/vault_document/{attachment['vault_document']}")
        doc = resp.json()

        resp = self.session.get(f"{self.url}/rest/download_attachment?vault_id={doc['hash']}")
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
            update_nested_dict(recording_pack, self.download_recording(attachments[i]))

    @staticmethod
    def get_session(username: str, password: str, verify_ssl: bool = False):
        s = Session()
        s.auth = HTTPBasicAuth(username, password)
        if not verify_ssl:
            s.verify = False
        return s

    @staticmethod
    def select_indexes():
        index_prompt = typer.prompt("Select attachments to download, comma-separated e.g. 1,2,3")
        return [int(i) for i in index_prompt.split(",")]

    @staticmethod
    def select_playbook():
        index_prompt = typer.prompt("Select a single playbook to download by id")
        try:
            return int(index_prompt)
        except ValueError:
            return None

    def get_attachments(self, container_id: int, max: int):
        print("Downloading Attachments")
        resp = self.session.get(
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
            if "scope" not in metadata:  # TODO Change to Asset Mocker version
                continue
            pb_run_id = metadata.get("playbook_run_id")
            if pb_run_id:
                pb_name = metadata.get("playbook_name")
                app_name = metadata.get("app_name")
                playbooks[f"{app_name}_{pb_name}_{pb_run_id}"].append(a)
            else:
                actions.append(a)
        return actions, playbooks
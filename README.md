# SOAR Asset Mocker
The SOAR Asset Mocker is an optional add-on for [SOAR connectors](https://github.com/splunk-soar-connectors) that enables the recording and replaying of connector transport. This functionality can lead to faster playbook development and reduced resource consumption.

# Table of Contents
1. [Quick start](#Quickstart)
2. [Connector Installation](#Installation)
3. [CLI](#CLI)
4. [Environmental Variables](#Environmental-Variables)
5. [Content redaction](#content-redaction)
6. [Limitations](#limitations)
7. [List of supported connectors](#list-of-supported-connectors)
8. [Contributing](#contributing)

# Installation

If you are developing a SOAR connector, you can add Asset Mocker to it.
Start by installing Asset Mocker
> pip install soar-asset-mocker

Now you have access to `soar-asset-mocker cli`, more about it under [cli chapter](#CLI).
To inject Asset Mocker to the connector just write the command below, with the right path to the connector's JSON file.
> soar-asset-mocker inject ./connector_directory/connector.json

After execution you can check what has been changed in your connector, you can expect a new import in main connector module and a new decorator:
```
from soar_asset_mocker import AssetMocker, MockType
...
class ExampleConnector(BaseConnector):
    ...
   @AssetMocker.use(MockType.HTTP)
   def handle_action(self, param):
    ...
```
You should also see `soar-asset-mocker` in `requirements.txt` file. Now you can commit your changes, recompile your app and load it into SOAR to enhance playbook development experience.

# Quickstart

Connector with Asset Mocker will not look and behave any different than any other connector by default. To enable Asset Mocker you have to add [envronmental variables](#environmental-variables) to your asset.

![Alt text](docs/images/env_vars.png)

To start recording actions from playbook runs just set `SOAR_AM_MODE` to `RECORD` and run playbook using your modified asset. 

After execution, recordings will be visible under container files.
![Alt text](docs/images/files.png)

Now we can use CLI to grab and merge all the recordings into one file, run the command presented below and follow the steps outputed by this command.

> soar-asset-mocker fetch <container_id> myrecordingname.mock

After preparing your mock file, you can upload it to any container in SOAR and point at it in asset configuration

![Alt text](docs/images/mocking_settings.png)

Now, with recorded connector's transport, you can run playbooks with mocked external APIs!

# CLI

CLI can be utilised to automate some parts of Asset Mocker workflow.
For now it supports 2 commands:
* Inject Asset Mocker into SOAR Connector.
    > soar-asset-mocker inject ./connector_directory/connector.json
    
    It will inject Asset Mocker into connectors code, together with updating dependencies. User is still required to check applied changes and run pre-commit actions.

* Download and merge recording files.
    > soar-asset-mocker fetch <container_id> myrecordingname.mock

    This command gathers recordings from SOAR container. Then, user selects which of them should be merged together into one file. After that, user can load that file into SOAR and start mocking with it.


# Environmental Variables

* **SOAR_AM_MODE** - RECORD|MOCK|NONE (default: NONE)
    * **RECORD** - Asset Mocker will record all HTTP traffic comming through Python sockets of connector process. 
    * **MOCK** - Requires a file name or vault id. It will load recording and use it to mock all HTTP traffic. It will throw an error if there is any new unrecorded traffic.
    * **NONE** - Asset Mocker is deactivated
* **SOAR_AM_SCOPE** - Sets the scope of work for mocker:
    * **ALL** - All actions on SOAR will be recorded/mocked
    * **VPE** - Only actions executed through VPE will be recorded/mocked (default)
* **SOAR_AM_CONTAINER_ID** - It determines where recordings will be stored. By default (no value), recordings will be stored in the same container that the action was executed in.
* **SOAR_AM_FILE_NAME** - A name of recording to be used for mocking. Mocking will fail if file is not found.
* **SOAR_AM_FILE_VAULT_ID** - Alternatively to file name, vault id can be used to query for uploaded recording. When file name and vault id are both provided, Asset Mocker will try to find a recording that match both fields.
* **SOAR_AM_FILE_CONTAINER_ID** - If there might be two the same file names for recordings, container ID can be specified to make the query more specific.

# Content redaction

* By default, recorded HTTP requests and responses contain redacted information such as tokens, emails, passwords, and other secrets. Instead of the actual value of that field, you'll see the `*ASSET_MOCKER_REDACTED*` string.

# Limitations

* Asset Mocker does not currently use the connector`s state. This means that a looped action in which the response changes each iteration might not get properly recorded.
* Asset Mocker cannot record traffic that happens outside of the Python runner. This means that communication done via a subprocess spawned by the connector can't be tracked.

# List of supported connectors

TBD

# Contributing

If you've found an improvement and wish to implement it, the steps to do so are as follows.

1. Fork the repo.
2. Install [pre-commit](https://pre-commit.com/#install) if it is not installed and then run `pre-commit install` while inside the Asset Mocker repo. Note: This step is not required, but strongly recommended! It will allow you to catch issues before even pushing any code.
3. Install [poetry](https://python-poetry.org/) and run `poetry install` while inside the repository.
4. Create a branch.
5. Implement your changes.
6. Add or amend existing unit tests as appropriate to verify your change.
7. Run tests locally - `poetry run pytest .`
8. Test Asset Mocker with any connector, for example [Censys Connector](https://github.com/splunk-soar-connectors/censys) can be used. Use `poetry shell` to access cli from your repo and follow [quick start](#Quickstart) to install and work with Asset Mocker.
9. Create a pull request to the next branch of the Asset Mocker's repo.

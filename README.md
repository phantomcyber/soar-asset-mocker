# SOAR Asset Mocker
SOAR Asset Mocker is an optional addon for SOAR connectors that allow for recording and replaying connectors transport. As a result you may expect faster playbook development and lower resource usage.

# Table of Contents
1. [Quick start](#Quickstart)
2. [Connector Installation](#Installation)
3. [CLI](#CLI)
4. [Options](#Options)
5. [Content redaction](#content-redaction)

# Installation

If you are developing SOAR connector, you can add Asset Mocker to it.
Start by installing Asset Mocker
> pip install soar-asset-mocker

Now you have access to `soar-asset-mocker cli`, more about it under [cli chapter](#CLI).
To automatically load Asset Mocker to connector just write the command below, with right access path for connector json file.
> soar-asset-mocker inject ./connector_directory/connector.json

After execution you can check what has changed in your connector, you can expect a new import in main connector module and a new decorator:
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

![Alt text](docs/images//env_vars.png)

To start recording actions from playbook runs just set `SOAR_AM_MODE` to `RECORD` and run playbook using your modified asset. 

After execution, recordings will be visible under container artifacts or files.
![Alt text](image.png)

Now we can use CLI to grab and merge all the recordings into one file, input command below and follow the steps.

> soar-asset-mocker fetch <container_id> myrecordingname.mock

After having file generated, 

# CLI

# Environmental Variables

* SOAR_AM_MODE = RECORD|MOCK|NONE (default: NONE)
* SOAR_AM_SCOPE = ALL|VPE (default: VPE)
* SOAR_AM_CONTAINER_ID
* SOAR_AM_FILE_NAME

# Recording file

# Content redaction

# Limitations

* Asset Mocker as of now does not make use of state. It means that looped action in which response changes each iteration might not get properly recorded.
* Asset Mocker cannot record any traffic that happens outside of Python runner. It means that any communication that is done via a subprocess spawned by connector can't be tracked.

# List of SOAR connectors with Asset Mocker

TBD

from enum import Enum
from os import getenv


class MockType(str, Enum):
    HTTP = "http"


class AssetMockerMode(str, Enum):
    NONE = "NONE"
    RECORD = "RECORD"
    MOCK = "MOCK"


class AssetMockerScope(str, Enum):
    ALL = "ALL"
    VPE = "VPE"


class EnvVariables:
    def __init__(self) -> None:
        # Variables are object attributes to make testing against env variables easier.
        # Having them as a class variables would require to patch
        # whole EnvVariables instead of just setting env variables.
        self.MODE = getenv("SOAR_AM_MODE", "NONE")
        self.SCOPE = getenv("SOAR_AM_SCOPE", "VPE")
        self.CONTAINER_ID = getenv("SOAR_AM_CONTAINER_ID")
        self.FILE_NAME = getenv("SOAR_AM_FILE_NAME", "")
        self.FILE_CONTAINER_ID = getenv("SOAR_AM_FILE_CONTAINER_ID", "")
        self.FILE_VAULT_ID = getenv("SOAR_AM_FILE_VAULT_ID", "")

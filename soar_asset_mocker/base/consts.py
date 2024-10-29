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
    MODE = getenv("SOAR_AM_MODE", "NONE")
    SCOPE = getenv("SOAR_AM_SCOPE", "VPE")
    CONTAINER_ID = getenv("SOAR_AM_CONTAINER_ID")
    FILE_NAME = getenv("SOAR_AM_FILE_NAME", "")
    FILE_CONTAINER_ID = getenv("SOAR_AM_FILE_CONTAINER_ID", "")
    FILE_VAULT_ID = getenv("SOAR_AM_FILE_VAULT_ID", "")

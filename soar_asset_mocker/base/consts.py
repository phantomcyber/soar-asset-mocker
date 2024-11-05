from enum import Enum
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as get_version


class MockType(str, Enum):
    HTTP = "http"


class AssetMockerMode(str, Enum):
    NONE = "NONE"
    RECORD = "RECORD"
    MOCK = "MOCK"


class AssetMockerScope(str, Enum):
    ALL = "ALL"
    VPE = "VPE"


try:
    ASSET_MOCKER_VERSION = get_version("soar_asset_mocker")
except PackageNotFoundError:
    # In case we inject development version, package may not be found.
    ASSET_MOCKER_VERSION = "dev-version"

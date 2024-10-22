from enum import Enum


class MockType(str, Enum):
    HTTP = "http"


class AssetMockerMode(str, Enum):
    NONE = "NONE"
    RECORD = "RECORD"
    MOCK = "MOCK"


class AssetMockerScope(str, Enum):
    ALL = "ALL"
    VPE = "VPE"

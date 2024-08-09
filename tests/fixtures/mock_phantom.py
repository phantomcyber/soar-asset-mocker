import sys
import types
from unittest.mock import Mock

module_name = "soar_asset_mocker.connector.soar_libs"
phantom_module = types.ModuleType(module_name)
sys.modules[module_name] = phantom_module
phantom_module.phantom = Mock(name=module_name + ".phantom")
phantom_module.Vault = Mock(name=module_name + ".Vault")

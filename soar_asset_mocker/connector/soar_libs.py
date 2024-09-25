try:
    import phantom.app as phantom
    from phantom.vault import Vault as Vault
    from phantom.vault import vault_info as vault_info

    phantom_available = True  # flag used to prohibid running core functionality without importing module
except ModuleNotFoundError:
    from unittest.mock import Mock

    phantom = Mock()
    Vault = Mock()
    vault_info = Mock()
    phantom_available = False

__all__ = ("phantom", "Vault", "phantom_available")

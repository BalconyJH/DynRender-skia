from unittest.mock import patch

import pytest
from loguru import logger


def import_module():
    import dynrender_skia  # noqa


def test_import_skia_success():
    with patch.dict("sys.modules", skia=object()):
        try:
            import_module()
        except ImportError:
            pytest.fail("ImportError raised unexpectedly!")


def test_import_skia_failure():
    with patch.dict("sys.modules", {"skia": None}):
        with patch.object(logger, "error") as mock_error, patch.object(logger, "warning") as mock_warning:
            with pytest.raises(RuntimeError, match="Dynrender runtime error"):
                import_module()

            mock_error.assert_called_once()
            mock_warning.assert_called_once()
            warning_message = (
                "Missing dependent files \n\n please install dependence: \n\n "
                "---------------------------------------\n\n "
                "Ubuntu: apt install libgl1-mesa-glx \n\n "
                "ArchLinux: pacman -S libgl \n\n "
                "Centos: yum install mesa-libGL -y \n\n"
                "---------------------------------------"
            )
            mock_warning.assert_called_with(warning_message)

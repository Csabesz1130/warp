import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(autouse=True)
def _reset_optix_settings():
    from optix.config import reset_settings

    reset_settings()
    yield
    reset_settings()

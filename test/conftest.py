import shutil

import pytest

@pytest.fixture(scope="session")
def shared_cache(tmp_path_factory):
    cache_dir = tmp_path_factory.mktemp("cache", numbered=False)
    yield cache_dir
    shutil.rmtree(cache_dir)
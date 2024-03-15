import shutil
from pathlib import Path
from dynrender.Core import DynRender  # 确保路径是正确的
from loguru import logger

import pytest


@pytest.fixture(scope="session")
def shared_cache(tmp_path_factory):
    cache_dir = tmp_path_factory.mktemp("cache", numbered=False)
    logger.info(f"创建共享缓存目录：{cache_dir}")
    yield cache_dir
    shutil.rmtree(cache_dir)
    logger.info(f"删除共享缓存目录：{cache_dir}")


@pytest.fixture(scope="session")
def resource_dir():
    return Path(__file__).parent / "res"


@pytest.fixture(scope="session")
def dynrender_instance(shared_cache):
    dynrender_instance = DynRender(static_path=str(shared_cache))
    logger.info("DynRender实例创建成功")
    return dynrender_instance

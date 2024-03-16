from pathlib import Path

import httpx
import pytest
import numpy as np
import pytest_asyncio
import respx

from dynrender.DynTools import merge_pictures, request_img


@pytest.mark.asyncio
class TestMergePictures:
    async def test_with_single_valid_image(self):
        img_list = [np.zeros([1080, 1080, 4], np.uint8)]
        result = await merge_pictures(img_list)
        assert np.array_equal(result, img_list[0])

    async def test_with_multiple_valid_images(self):
        img1 = np.zeros([1080, 1080, 4], np.uint8)
        img2 = np.ones([1080, 1080, 4], np.uint8)
        img_list = [img1, img2]
        result = await merge_pictures(img_list)
        expected = np.vstack((img1, img2))
        assert np.array_equal(result, expected)

    async def test_with_some_invalid_images(self):
        img1 = np.zeros([1080, 1920, 4], np.uint8)  # Invalid width
        img2 = None  # None image
        img_list = [img1, img2]
        with pytest.raises(ValueError) as exc_info:
            await merge_pictures(img_list)
        assert "The width of the image must be 1080" in str(exc_info.value)

    async def test_with_all_invalid_images(self):
        img_list = [None, None]
        result = await merge_pictures(img_list)
        expected = np.zeros([0, 1080, 4], np.uint8)
        assert np.array_equal(result, expected)

    async def test_with_empty_list(self):
        img_list = []
        result = await merge_pictures(img_list)
        expected = np.zeros([0, 1080, 4], np.uint8)
        assert np.array_equal(result, expected)


@pytest.mark.asyncio
async def test_request_img_with_respx(resource_dir):
    with respx.mock() as mock:
        url = "http://bilibili.com"

        img_path = Path(resource_dir / "bilibili.png")
        img_content = img_path.read_bytes()

        route = mock.get(url)
        route.respond(content=img_content, status_code=200)

        async with httpx.AsyncClient() as client:
            size = (100, 100)
            img = await request_img(client, url, size)

            assert img.height() == 100 and img.width() == 100


@pytest.mark.asyncio
async def test_request_img_with_respx_invalid_url():
    with respx.mock() as mock:
        url = "http://bilibili.com"

        mock.get(url).mock(side_effect=httpx.ConnectError("Connection error"))

        async with httpx.AsyncClient() as client:
            img = await request_img(client, url, None)
            assert img is None


@pytest.mark.asyncio
class TestRequestImg:
    @pytest_asyncio.fixture(scope="session")
    async def client(self):
        async with httpx.AsyncClient() as client_instance:
            yield client_instance

    @pytest.fixture
    def img_url(self):
        return "http://bilibili.com"

    @pytest.fixture
    def img_path(self, resource_dir):
        return Path(resource_dir / "bilibili.png")

    async def test_request_img_success(self, client, img_url, img_path):
        async with respx.mock() as mock:
            img_content = img_path.read_bytes()
            mock.get(img_url).respond(content=img_content, status_code=200)
            size = (100, 100)
            img = await request_img(client, img_url, size)
            assert img.height() == 100 and img.width() == 100

    async def test_request_img_with_respx_invalid_url(self, client, img_url):
        async with respx.mock(base_url=img_url) as mock:
            mock.get(img_url).mock(side_effect=httpx.ConnectError("Connection error"))

            img = await request_img(client, img_url, None)
            assert img is None

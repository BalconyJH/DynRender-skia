import pathlib
from pathlib import Path

import httpx
import numpy as np
import pytest
import pytest_asyncio
import respx
import skia

from dynrender_skia.DynTools import merge_pictures, request_img, get_pictures


@pytest.mark.asyncio
class TestMergePictures:
    async def test_with_single_valid_image(self) -> None:
        img_list = [np.zeros([1080, 1080, 4], np.uint8)]
        result = await merge_pictures(img_list)
        assert np.array_equal(result, img_list[0])

    async def test_with_multiple_valid_images(self) -> None:
        img1 = np.zeros([1080, 1080, 4], np.uint8)
        img2 = np.ones([1080, 1080, 4], np.uint8)
        img_list = [img1, img2]
        result = await merge_pictures(img_list)
        expected = np.vstack((img1, img2))
        assert np.array_equal(result, expected)

    async def test_with_some_invalid_images(self) -> None:
        img1 = np.zeros([1080, 1920, 4], np.uint8)
        img2 = None
        img_list = [img1, img2]
        with pytest.raises(ValueError, match="The width of the image must be 1080") as exc_info:
            await merge_pictures(img_list)
        assert "The width of the image must be 1080" in str(exc_info.value)

    async def test_with_all_invalid_images(self) -> None:
        img_list = [None, None]
        result = await merge_pictures(img_list)  # type: ignore
        expected = np.zeros([0, 1080, 4], np.uint8)
        assert np.array_equal(result, expected)

    async def test_with_empty_list(self) -> None:
        img_list = []
        result = await merge_pictures(img_list)
        expected = np.zeros([0, 1080, 4], np.uint8)
        assert np.array_equal(result, expected)


@pytest.mark.asyncio
async def test_request_img_with_respx(resource_dir: pathlib.Path) -> None:
    with respx.mock() as mock:
        url = "http://bilibili.com"

        img_path = Path(resource_dir / "bilibili.png")
        img_content = img_path.read_bytes()

        route = mock.get(url)
        route.respond(content=img_content, status_code=200)

        async with httpx.AsyncClient() as client:
            size = (100, 100)
            img = await request_img(client, url, size)

            if img is None:
                return
            assert img.height() == 100
            assert img.width() == 100


@pytest.mark.asyncio
async def test_request_img_with_respx_invalid_url() -> None:
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

    async def test_request_img_success(
        self, client: httpx.AsyncClient, mock_img_url: str, img_path: pathlib.Path
    ) -> None:
        async with respx.mock() as mock:
            img_content = img_path.read_bytes()
            mock.get(mock_img_url).respond(content=img_content, status_code=200)
            size = (100, 100)
            img = await request_img(client, mock_img_url, size)
            if img is None:
                return
            assert img.height() == 100
            assert img.width() == 100

    async def test_request_img_with_exception(self, client: httpx.AsyncClient, mock_img_url: str) -> None:
        async with respx.mock(base_url=mock_img_url) as mock:
            mock.get(mock_img_url).mock(side_effect=httpx.ConnectError("Connection error"))

            img = await request_img(client, mock_img_url, None)
            assert img is None

    async def test_skia_encode_error(self, client: httpx.AsyncClient, mock_img_url: str, caplog) -> None:
        async with respx.mock() as mock:
            img_content = None
            mock.get(mock_img_url).respond(content=img_content, status_code=200)
            img = await request_img(client, mock_img_url, None)
            assert "Image decode error or request returned none in content" in caplog.text


@pytest.mark.asyncio
class TestGetPictures:
    @pytest.fixture
    def mock_skia_image(self, img_path: Path):
        return skia.Image.MakeFromEncoded(encoded=img_path.read_bytes())  # type: ignore

    async def test_get_pictures_with_single_url(
        self, mock_img_url: str, img_path: pathlib.Path, mock_skia_image: skia.Image
    ) -> None:
        async with respx.mock(base_url=mock_img_url) as mock:
            img_content = img_path.read_bytes()
            mock.get(mock_img_url).respond(content=img_content, status_code=200)
            image: skia.Image = await get_pictures(mock_img_url, None)

            img_array = image.tobytes()
            result = mock_skia_image.tobytes()
            assert img_array == result

    async def test_get_pictures_with_multiple_urls(self, mock_img_url: str, img_path: pathlib.Path) -> None:
        async with respx.mock(base_url=mock_img_url) as mock:
            img_content = img_path.read_bytes()
            mock.get(mock_img_url).respond(content=img_content, status_code=200)

            img_list = await get_pictures([mock_img_url, mock_img_url], None)
            assert len(img_list) == 2
            assert all(img is not None for img in img_list)

import pytest
import numpy as np
from dynrender.DynTools import merge_pictures

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

# @Time    : 2023/7/15 下午9:22
# @Author  : Polyisoprene
# @File    : DynTools.py
import asyncio
from typing import Optional, Union

import emoji
import httpx
import numpy as np
import skia
from loguru import logger
from numpy import ndarray

from .DynStyle import PolyStyle


async def get_pictures(
    url: Union[str, list[str]], size: Optional[tuple[int, int]] = None, retries: int = 5
) -> Union[skia.Image, tuple[skia.Image, ...]]:
    """
    Asynchronously fetch images from a single URL or a list of URLs, optionally resizing them.

    This function creates an HTTP client with a specified retry policy, fetches images from
    the given URLs, and optionally resizes them to the specified dimensions using the skia library.

    Args:
        url (Union[str, list[str]]): A single URL or a list of URLs from which to fetch images.
        size (Optional[tuple[int, int]]): A tuple specifying the width and height to which the images should be
        resized. If None, images are returned in their original size.
        retries (int): The number of times to retry the request in case of connection issues. Default is 5 retries.

    Returns:
        Union[skia.Image, tuple[skia.Image, ...]]: A single skia.Image if a single URL is provided, or a tuple of
        skia.Images if a list of URLs is provided. If any request fails or an image cannot be decoded,
        the corresponding return value will be None.

    Raises:
        httpx.HTTPStatusError: If any HTTP request returns an unsuccessful status code.
        Exception: If an unexpected error occurs during the fetching or decoding of images.
    """
    transport = httpx.AsyncHTTPTransport(retries=retries)
    async with httpx.AsyncClient(transport=transport) as client:
        if isinstance(url, list):
            return await asyncio.gather(*[request_img(client, i, size) for i in url])
        else:
            return await request_img(client, url, size)


async def request_img(client: httpx.AsyncClient, url: str, size: Optional[tuple[int, int]]) -> Optional[skia.Image]:
    """
    Request an image from a URL and optionally resize it.

    This function attempts to fetch an image from a specified URL using the provided httpx client,
    decode it into a skia.Image, and resize it if a size is specified.

    Args:
        client (httpx.AsyncClient): The HTTP client to use for the request.
        url (str): The URL from which to fetch the image.
        size (Optional[tuple[int, int]]): A tuple specifying the width and height to which the image should be
        resized. If None, the image is returned in its original size.

    Returns:
        Optional[skia.Image]: The fetched and resized skia.Image, or None if the image could not be fetched or decoded.

    Raises:
        httpx.HTTPStatusError: If the HTTP request returns an unsuccessful status code.
        Exception: If an unexpected error occurs during the fetching or decoding of the image.
    """
    try:
        response = await client.get(url)
        img: skia.Image = skia.Image.MakeFromEncoded(response.content)  # type: ignore
        if img is None:
            logger.error("Image decode error or request returned none in content")
        return img.resize(*size) if size is not None else img
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.exception(f"Request or HTTP error occurred: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return None


async def merge_pictures(img_list: list[ndarray]) -> ndarray:
    img_top = np.zeros([0, 1080, 4], np.uint8)
    if len(img_list) == 1 and img_list[0] is not None:
        return img_list[0]
    for img in img_list:
        if img is None:
            continue
        if img.shape[1] != 1080:
            raise ValueError("The width of the image must be 1080")
        img_top = np.vstack((img_top, img))
    return img_top


async def paste(canvas: skia.Canvas, target: skia.Image, position: tuple, clear_background: bool = False) -> None:
    """
    Paste the target image onto the canvas at the specified position, with an option to clear the background.

    Args:
        canvas (skia.Canvas): The canvas on which the image will be drawn.
        target (skia.Image): The image to be pasted onto the canvas.
        position (tuple): A tuple (x, y) is the position on the canvas where the top-left corner of the image will be
        placed.
        clear_background (bool): If set to True, the background aera where the image will be placed is cleared to
        transparent before pasting the image. Defaults to False.

    Raises:
        ValueError: If the `target` image is None.
        AttributeError: If there is an issue accessing attributes or methods on `canvas` or `target`.

    Returns:
        None: The function does not return a value, but modifies the canvas in place.
    """
    if target is None:
        raise ValueError("Target image is None.")

    x, y = position
    img_height = target.dimensions().fHeight
    img_width = target.dimensions().fWidth
    rec = skia.Rect.MakeXYWH(x, y, img_width, img_height)  # type: ignore

    try:
        if clear_background:
            canvas.save()
            canvas.clipRect(rec, skia.ClipOp.kIntersect)
            canvas.clear(skia.Color(*(255, 255, 255, 0)))

        canvas.drawImageRect(target, skia.Rect(0, 0, img_width, img_height), rec)

        if clear_background:
            canvas.restore()

    except (ValueError, AttributeError) as e:
        logger.exception(f"Failed to paste image: {e!s}")


class DrawText:
    def __init__(self, style: PolyStyle):
        self.style = style
        self.text_font = skia.Font(
            skia.Typeface.MakeFromName(self.style.font.font_family, self.style.font.font_style),
            self.style.font.font_size.text,
        )
        self.emoji_font = skia.Font(
            skia.Typeface.MakeFromName(self.style.font.emoji_font_family, self.style.font.font_style),
            self.style.font.font_size.text,
        )

    @staticmethod
    def initialize_paint(font_color: tuple[int, int, int, int]) -> skia.Paint:
        """
        Initialize a Paint object with the specified font color.
        """
        return skia.Paint(AntiAlias=True, Color=skia.Color(*font_color))

    @staticmethod
    def draw_ellipsis(canvas: skia.Canvas, x: int, y: int, font: skia.Font, paint: skia.Paint):
        """
        Draw an ellipsis at the specified position using the provided font and paint.
        """
        blob: skia.TextBlob = skia.TextBlob("...", font)  # type: ignore
        canvas.drawTextBlob(blob, x, y, paint)  # type: ignore

    def match_font(self, char: str, font_size: int) -> Optional[skia.Font]:
        """
        Matches a font for a given character and font size.

        This method uses the Skia Font Manager to find an appropriate font for the specified
        character based on the provided font size. It attempts to match a font that supports
        the character, considering the font family and style defined in the object's `style` attribute.

        Args:
            char (str): The character for which to find a matching font. Should be a single character string.
            font_size (int): The desired font size for the matched font.

        Returns:
            Optional[skia.Font]: A Skia `Font` object if a matching typeface is
            found, otherwise `None`.
        """
        if typeface := skia.FontMgr().matchFamilyStyleCharacter(
            self.style.font.font_family,
            self.style.font.font_style,
            ["zh", "en"],
            ord(char),
        ):
            return skia.Font(typeface, font_size)
        return None

    def set_font_sizes(self, font_size: int):
        """
        Set the font sizes for the text and emoji fonts.
        """
        self.text_font.setSize(font_size)
        self.emoji_font.setSize(font_size)

    async def extract_emoji_info(self, text: str) -> tuple[str, dict[int, list[Union[int, str]]]]:
        """
        Removes tabs from the given text and extracts emoji information.

        This function removes all tab characters from the provided text, then extracts
        and processes information about any emojis present in the text. It returns
        the cleaned text and a dictionary containing the emoji information.

        Args:
            text (str): The input text containing possible emojis.

        Usage:
        ```python
        text = "Hello, 🌍!"
        cleaned_text, emoji_info = await extract_emoji_info(text)
        print(cleaned_text)
        print(emoji_info)
        # Output: "Hello, 🌍!", {7: [8, '🌍']}
        ```

        Returns:
            tuple: A tuple containing:
                - The cleaned text without tab characters (str).
                - A dictionary with keys as integer positions of emojis in the text,
                  and values as lists containing the emoji index and the corresponding
                  emoji string (dict[int, list[Union[int, str]]]).
        """
        text = text.replace("\t", "")
        emoji_info: dict[int, list[Union[int, str]]] = await self.get_emoji_text(text)
        return text, emoji_info

    @staticmethod
    async def get_emoji_text(text: str) -> dict[int, list[Union[int, str]]]:
        """
        Get the positions of emojis in the text and their corresponding Unicode characters.

        Args:
            text (str): The text in which to search for emojis.

        Usage:
        ```python
        text = "Hello, 🌍!"
        emoji_info = await get_emoji_text(text)
        print(emoji_info)
        # Output: {7: [8, '🌍']}
        ```

        Returns:
            dict[int, list[Union[int, str]]]: A dictionary with the starting position of each emoji in the text as the key,
            and a list containing the end position of the emoji and the emoji character as the value.
        """
        result = emoji.emoji_list(text)
        return {i["match_start"]: [i["match_end"], i["emoji"]] for i in result}

    async def draw_text(
        self,
        canvas: skia.Canvas,
        text: str,
        font_size: int,
        pos: tuple[int, int, int, int, int],
        font_color: tuple[int, int, int, int],
    ):
        self.set_font_sizes(font_size)
        paint = self.initialize_paint(font_color)

        text, emoji_info = await self.extract_emoji_info(text)
        total = len(text) - 1
        x, y, x_bound, y_bound, y_int = pos
        offset: int = 0

        while offset <= total:
            j = text[offset]
            if j == "\n":
                break

            if offset in emoji_info:
                j = emoji_info[offset][1]
                end_pos = emoji_info[offset][0]
                if isinstance(end_pos, int):
                    offset = end_pos
                else:
                    raise TypeError(f"Expected integer for offset end position, got {type(end_pos).__name__}")
                font = self.emoji_font
            else:
                offset += 1
                font = self.text_font

            if isinstance(j, str) and font.textToGlyphs(j)[0] == 0:
                font = self.match_font(j, font_size) or self.text_font

            measure = font.measureText(j)
            blob = skia.TextBlob(j, font)
            canvas.drawTextBlob(blob, x, y, paint)
            x += measure

            if x > x_bound:
                y += y_int
                if y >= y_bound:
                    self.draw_ellipsis(canvas, x, y - y_int, font, paint)
                    break
                x = pos[0]

    @staticmethod
    async def get_emoji_text(text: str) -> dict[int, list[Union[int, str]]]:
        result = emoji.emoji_list(text)
        return {i["match_start"]: [i["match_end"], i["emoji"]] for i in result}

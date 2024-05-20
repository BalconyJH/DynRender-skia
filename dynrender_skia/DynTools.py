# @Time    : 2023/7/15 下午9:22
# @Author  : Polyisoprene
# @File    : DynTools.py
import asyncio
import platform
import sys
from typing import List, Optional, Union, Tuple, Dict

import emoji
import httpx
import numpy as np
import skia
from loguru import logger
from numpy import ndarray

from .DynStyle import PolyStyle


def get_sys_info():
    system_info = {
        "System Type": platform.system(),
        "Bitness": platform.architecture()[0],
        "Python Version": sys.version.split()[0],
        "Architecture": platform.machine(),
    }

    try:
        import skia

        system_info["Skia-Python Version"] = skia.__version__
    except ImportError as e:
        logger.exception(e)
        logger.warning(
            "Missing dependent files \n\n please install dependence: \n\n ---------------------------------------\n\n "
            "Ubuntu: apt install libgl1-mesa-glx \n\n ArchLinux: pacman -S libgl \n\n Centos: yum install mesa-libGL -y "
            "\n\n---------------------------------------"
        )
        system_info["Skia-Python Version"] = ""
    except Exception as e:
        logger.exception(e)
        system_info["Skia-Python Version"] = ""

    return system_info


async def get_pictures(
    url: Union[str, List[str]], size: Optional[Tuple[int, int]] = None
) -> Union[skia.Image, Tuple[skia.Image, ...]]:
    async with httpx.AsyncClient() as client:
        if isinstance(url, list):
            return await asyncio.gather(*[request_img(client, i, size) for i in url])
        elif isinstance(url, str):
            return await request_img(client, url, size)


async def request_img(client: httpx.AsyncClient, url: str, size: Optional[Tuple[int, int]]) -> Optional[skia.Image]:
    """
    Request image from url and return skia.Image

    Args:
        client: httpx.AsyncClient
        url: str
        size: Optional[Tuple[int, int]]

    Returns:
        Optional[skia.Image]: skia.Image
    """
    try:
        resp = await client.get(url)
        if resp.status_code != 200:
            raise httpx.HTTPStatusError(
                f"Request failed with status code {resp.status_code}", request=resp.request, response=resp
            )
        img = skia.Image.MakeFromEncoded(encoded=resp.content)  # type: ignore
        if img is None:
            logger.error("Failed to decode image")
            return None
        return img.resize(*size) if size is not None else img
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.exception(f"Request or HTTP error occurred: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
    return None


async def merge_pictures(img_list: List[ndarray]) -> ndarray:
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


async def paste(src, target, position: tuple) -> None:
    try:
        if target is not None:
            x, y = position
            img_height = target.dimensions().fHeight
            img_width = target.dimensions().fWidth
            rec = skia.Rect.MakeXYWH(x, y, img_width, img_height)
            src.drawImageRect(target, skia.Rect(0, 0, img_width, img_height), rec)
    except Exception as e:
        logger.exception(e)


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

    async def draw_text(self, canvas, text: str, font_size, pos: tuple, font_color: tuple):
        paint = skia.Paint(AntiAlias=True, Color=skia.Color(*font_color))
        self.text_font.setSize(font_size)
        self.emoji_font.setSize(font_size)
        text = text.replace("\t", "")
        emoji_info = await self.get_emoji_text(text)
        total = len(text) - 1
        x, y, x_bound, y_bound, y_int = pos
        offset = 0
        while offset <= total:
            j = text[offset]
            if j == "\n":
                break
            if offset in emoji_info.keys():
                j = emoji_info[offset][1]
                offset = emoji_info[offset][0]
                font = self.emoji_font
            else:
                offset += 1
                font = self.text_font
            if font.textToGlyphs(j)[0] == 0:
                if typeface := skia.FontMgr().matchFamilyStyleCharacter(
                    self.style.font.font_family,
                    self.style.font.font_style,
                    ["zh", "en"],
                    ord(j[0]),
                ):
                    font = skia.Font(typeface, font_size)
                else:
                    font = self.text_font
            measure = font.measureText(j)
            blob = skia.TextBlob(j, font)
            canvas.drawTextBlob(blob, x, y, paint)
            x += measure
            if x > x_bound:
                y += y_int
                if y >= y_bound:
                    blob = skia.TextBlob("...", font)
                    canvas.drawTextBlob(blob, x, y - y_int, paint)
                    break
                x = pos[0]

    @staticmethod
    async def get_emoji_text(text: str) -> Dict[int, List[Union[int, str]]]:
        result = emoji.emoji_list(text)
        return {i["match_start"]: [i["match_end"], i["emoji"]] for i in result}


async def draw_shadow(canvas, pos: tuple, corner: int, bg_color):
    x, y, width, height = pos
    rec = skia.Rect.MakeXYWH(x, y, width, height)
    paint = skia.Paint(
        Color=skia.Color(*bg_color),
        AntiAlias=True,
        ImageFilter=skia.ImageFilters.DropShadow(0, 0, 10, 10, skia.Color(120, 120, 120)),
    )
    if corner != 0:
        canvas.drawRoundRect(rec, corner, corner, paint)
    else:
        canvas.drawRect(rec, paint)

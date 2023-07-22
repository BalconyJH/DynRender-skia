# -*- coding: utf-8 -*-
# @Time    : 2023/7/15 下午9:22
# @Author  : Polyisoprene
# @File    : DynTools.py
import asyncio
from typing import List, Optional, Union

import emoji
import httpx
import numpy as np
import skia
from loguru import logger
from numpy import ndarray

from .DynStyle import PolyStyle


async def get_pictures(url: Union[str, list], size: Optional[tuple] = None):
    async with httpx.AsyncClient() as client:
        if isinstance(url, list):
            return await asyncio.gather(*[request_img(client, i, size) for i in url])
        elif isinstance(url, str):
            return await request_img(client, url, size)


async def request_img(client, url, size):
    try:
        resp = await client.get(url)
        assert resp.status_code == 200
        img = skia.Image.MakeFromEncoded(resp.content)
        if size is not None and img is not None:
            return img.resize(*size)
        return img

    except:
        logger.exception("e")
        return None

        #     pas


async def merge_pictures(img_list: List[ndarray]) -> ndarray:
    img_top = np.zeros([0, 1080, 4], np.uint8)
    if len(img_list) == 1 and img_list[0] is not None:
        return img_list[0]
    for i in img_list:
        if i is not None:
            img_top = np.vstack((img_top, i))
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
        self.text_font = skia.Font(skia.Typeface.MakeFromName(self.style.font.font_family, self.style.font.font_style),
                                   self.style.font.font_size.text)
        self.emoji_font = skia.Font(
            skia.Typeface.MakeFromName(self.style.font.emoji_font_family, self.style.font.font_style),
            self.style.font.font_size.text)

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

    async def get_emoji_text(self, text):
        result = emoji.emoji_list(text)
        temp = {}
        for i in result:
            temp[i["match_start"]] = [i["match_end"], i["emoji"]]
        return temp

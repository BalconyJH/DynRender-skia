# -*- coding: utf-8 -*-
# @Time    : 2023/7/15 下午9:22
# @Author  : Polyisoprene
# @File    : DynTools.py
import asyncio
from typing import List, Optional, Union
import httpx
import numpy as np
from numpy import ndarray
import skia
from loguru import logger


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
    x, y = position
    img_height = target.dimensions().fHeight
    img_width = target.dimensions().fWidth
    rec = skia.Rect.MakeXYWH(x, y, img_width, img_height)
    src.drawImageRect(target, skia.Rect(0, 0, img_width, img_height), rec)

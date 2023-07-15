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


async def get_pictures(url: Union[str,list], size: Optional[tuple] = None):
    async with httpx.AsyncClient() as client:
        # resp = await client.get(url)
        if isinstance(url, list):
            return await asyncio.gather(*[request_img(client, i, size) for i in url])
        else:
            return await request_img(client, url, size)


async def request_img(client, url, size):
    try:
        resp = client.get(url)
        assert resp.status_code == 200
        img = skia.Image.MakeFromEncoded(resp.content).convert(alphaType=skia.AlphaType.kPremul_AlphaType)
        if size is not None:
            return img.resize(*size)
    except:
        return None

        #     pas


async def merge_pictures(img_list: List[ndarray]) -> ndarray:
    img_top = None
    if len(img_list) == 1 and img_list[0] is not None:
        return img_list[0]
    for i, j in enumerate(img_list):
        if i == 0:
            img_top = j
        else:
            try:
                img_top = np.vstack((img_top, j))
            except ValueError:
                print(j)
    return img_top


async def paste(src, target, position: tuple) -> None:
    x, y = position
    img_height = target.dimensions().fHeight
    img_width = target.dimensions().fWidth
    rec = skia.Rect.MakeXYWH(x, y, img_width, img_height)
    src.drawImageRect(target, skia.Rect(0, 0, img_width, img_height), rec)

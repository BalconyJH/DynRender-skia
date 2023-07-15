# -*- coding: utf-8 -*-
# @Time    : 2023/7/15 下午8:12
# @Author  : Polyisoprene
# @File    : DynText.py

from os import path

import emoji
import skia
import asyncio
import numpy as np
from typing import Optional
from loguru import logger
from .DynStyle import PolyStyle
from dynamicadaptor.Content import Text


class BiliText:
    """渲染动态的文字部分"""

    def __init__(self, static_path: str, style: PolyStyle) -> None:
        self.emoji_path = path.join(static_path, "Cache", "Emoji")
        self.src_path = path.join(static_path, "Src")
        self.style = style
        surface = skia.Surface(1080, 60)
        self.canvas = surface.getCanvas()
        self.offset = 40
        self.x_bound = 1040
        self.image_list = []

    async def run(self, dyn_text: Text, repost: bool = False) -> Optional[np.ndarray]:
        background_color = self.style.color.background.repost if repost else self.style.color.background.normal
        self.canvas.clear(skia.Color(*background_color))
        try:
            tasks = []
            if dyn_text.topic is not None:
                pass
            if dyn_text.text:
                tasks.append(self.draw_text())
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.exception("Error")
            return None

    async def draw_text(self, text: str, color: tuple):
        pass

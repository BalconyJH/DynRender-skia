from os import path

import emoji
import skia
import asyncio
import numpy as np
from typing import Optional
from loguru import logger
from .DynStyle import PolyStyle
from .DynTools import paste, merge_pictures, get_pictures
from dynamicadaptor.Majors import Major


class BiliMajor:
    def __init__(self, static_path: str, style: PolyStyle) -> None:
        self.src_path = path.join(static_path, "Src")
        self.style = style

    async def run(self, dyn_major: Major, repost: bool = False) -> Optional[np.ndarray]:
        try:
            major_type = dyn_major.type
            print(major_type)
        except Exception as e:
            logger.exception(e)
            return None

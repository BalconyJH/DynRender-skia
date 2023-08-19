# -*- coding: utf-8 -*-
'''
@File    :   Core.py
@Time    :   2023/07/13 15:21:46
@Author  :   Polyisoprene 
@Version :   1.0
@Desc    :   None
'''
import asyncio

from dynamicadaptor.Message import RenderMessage

from .DynAdditional import BiliAdditional
from .DynConfig import MakeStaticFile, SetDynStyle
from .DynHeader import BiliHeader, Footer
from .DynMajor import BiliMajor
from .DynRepost import BiliRepost
from .DynText import BiliText
from .DynTools import merge_pictures


class DynRender:
    def __init__(self, font_family: str = "Noto Sans CJK SC",
                 emoji_font_family: str = "Noto Color Emoji",
                 font_style: str = "Normal",
                 static_path: str = None) -> None:
        """create static file and set font family and font style

        Args:
            font_family (str, optional): font family name like "Noto Sans CJK SC". Defaults to "Noto Sans CJK SC".
            emoji_font_family (str, optional):emoji font family name like "Noto Color Emoji". Defaults to "Noto Sans CJK SC".
            font_style (str, optional): font style like "Normal、Bold、Italic、BoldItalic". Defaults to "Normal".
            static_path (str, optional): static file path,must be absolute path. Defaults to None.
        """
        self.static_path = MakeStaticFile(static_path).check_cache_file
        self.style = SetDynStyle(font_family, emoji_font_family, font_style).set_style

    async def run(self, message: RenderMessage):
        tasks = [BiliHeader(self.static_path, self.style).run(message.header)]
        if message.text is not None:
            tasks.append(BiliText(self.static_path, self.style).run(message.text))
        if message.major is not None:
            tasks.append(BiliMajor(self.static_path, self.style).run(message.major))

        if message.forward is not None:
            tasks.append(BiliRepost(self.static_path, self.style).run(message.forward))

        if message.additional is not None:
            tasks.append(BiliAdditional(self.static_path, self.style).run(message.additional))

        tasks.append(Footer(self.static_path, self.style).run())
        result = await asyncio.gather(*tasks)
        return await merge_pictures(result)

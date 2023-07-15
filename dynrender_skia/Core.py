#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   Core.py
@Time    :   2023/07/13 15:21:46
@Author  :   Polyisoprene 
@Version :   1.0
@Desc    :   None
'''

from dynamicadaptor.Message import RenderMessage

from .DynConfig import MakeStaticFile, SetDynStyle
from .DynHeader import BiliHeader


class DynRender:
    def __init__(self, font_family: str = "Noto Sans CJK SC", font_style: str = "Normal",
                 static_path: str = None) -> None:
        """creat static file and set font family and font style

        Args:
            font_family (str, optional): font family name like "Noto Sans CJK SC". Defaults to "Noto Sans CJK SC".
            font_style (str, optional): font style like "Normal、Bold、Italic、BoldItalic". Defaults to "Normal".
            static_path (str, optional): static file path,must be absolute path. Defaults to None.
        """
        self.static_path = MakeStaticFile(static_path).check_cache_file
        self.style = SetDynStyle(font_family, font_style).set_style

    async def run(self, message: RenderMessage):
        task = BiliHeader(self.static_path, self.style)
        return await task.run(message.header)

# -*- coding: utf-8 -*-
'''
@File    :   DynRepost.py
@Time    :   2023/07/19 15:33:23
@Author  :   Polyisoprene 
@Version :   1.0
@Desc    :   None
'''
from dynamicadaptor.Repost import Forward
from .DynHeader import RepostHeader
from .DynText import BiliText
from .DynTools import merge_pictures
from .DynMajor import BiliMajor
from .DynStyle import PolyStyle
import asyncio

class BiliRepost:
    def __init__(self, static_path: str, style: PolyStyle) -> None:
        self.static_path = static_path
        self.style = style
    
    async def run(self,message: Forward):
        tasks = [RepostHeader(self.static_path,self.style).run(message.header)]
        if message.text is not None:
            tasks.append(BiliText(self.static_path, self.style).run(message.text,repost=True))
        if message.major is not None:
            tasks.append(BiliMajor(self.static_path, self.style).run(message.major,True))
        result = await asyncio.gather(*tasks)
        return await merge_pictures(result)
        
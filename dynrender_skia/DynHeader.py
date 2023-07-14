import asyncio
from os import path
from typing import Optional

import numpy as np
import skia
from dynamicadaptor.Header import Head
from DynConfig import logger
from DynStyle import PolyStyle


class BiliHeader:
    def __init__(self,static_path:str,style:PolyStyle,header_message) -> None:
        self.face_path = path.join(static_path,"Cache","Face")
        self.emoji_path = path.join(static_path,"Cache","Emoji")
        self.pendant_path = path.join(static_path,"Cache","Pendant")
        self.src_path = path.join(static_path,"Src")
        self.style = style
        self.canvas = None
        self.message = None
    
    async def run(self,header_message:Head) -> Optional[np.ndarray]:
        try:
            self.message = header_message
            surface = skia.Surface(1080,400)
            self.canvas = surface.getCanvas()
            self.canvas.clear(skia.Color(*self.style.color.backgroud.normal))
            
        except Exception:
            logger.exception("Error")
            return None
    
    async def paste_logo(self) -> None:
        
        logo = skia.Image.open(path.join(self.src_path, "bilibili.png")).convert(alphaType=skia.kUnpremul_AlphaType).resize(231, 105)
        
        await self.paste(self.canvas,logo,(433, 20))
    
    
    async def draw_name(self):
        # 如果是大会员的话
        if self.message.vip and self.message.vip.status == 1:
            # 如果是大会员名字是粉色
            if self.message.vip.avatar_subscript == 1:
                color = self.style.color.font_color.name_big_vip
            else:
                # 到了愚人节大会员名字会变成绿色
                color = self.style.color.font_color.name_small_vip
        else:
            color = self.style.color.font_color.text
        skia_color = skia.Color(*color)
        for i in self.message.name:
            pass
    
    async def paste(self,canvas,image,position):
        x,y = position
        img_height = image.dimensions().fHeight
        img_width = image.dimensions().fWidth
        rec = skia.Rect.MakeXYWH(x,y,img_width,img_height)
        canvas.drawImageRect(image,skia.Rect(0, 0,img_width, img_height),rec)
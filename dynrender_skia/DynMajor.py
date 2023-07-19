# -*- coding: utf-8 -*-
'''
@File    :   DynMajor.py
@Time    :   2023/07/16 20:21:46
@Author  :   Polyisoprene
@Version :   1.0
@Desc    :   None
'''
from os import path

import skia
import numpy as np
from typing import Optional
from loguru import logger
from .DynStyle import PolyStyle
from .DynTools import paste, merge_pictures, get_pictures
from dynamicadaptor.Majors import Major
from math import ceil


from abc import ABC, abstractmethod


class AbstractMajor(ABC):
    def __init__(self,src_path: str,style: PolyStyle, dyn_major: Major) -> None:
        self.style = style
        self.major = dyn_major
        self.text_font = skia.Font(skia.Typeface.MakeFromName(self.style.font.font_family,self.style.font.font_style),self.style.font.font_size.text)
        self.emoji_font = skia.Font(skia.Typeface.MakeFromName(self.style.font.emoji_font_family,self.style.font.font_style),self.style.font.font_size.text)    
        self.src_path = src_path
        
        
    @abstractmethod
    async def run(self,repost):
        pass
    
    async def draw_text(self):
        pass
    
    async def draw_shadow(self,canvas,pos:tuple,corner:int):
        x,y,width,height= pos
        rec = skia.Rect.MakeXYWH(x,y,width,height)
        paint = skia.Paint(
        Color=skia.Color(255,255,255),
        AntiAlias=True,
        ImageFilter=skia.ImageFilters.DropShadow(3, 3, 3, 3, skia.Color(120,120,120))
        )
        if corner != 0:
            canvas.drawRoundRect(rec, corner, corner, paint)
        else:
            canvas.drawRect(rec,paint)
        
    
    async def make_round_cornor(self,img,corner:int):
        surface = skia.Surface(img.dimensions().fWidth,img.dimensions().fHeight)
        mask = surface.getCanvas()
        paint = skia.Paint(
            Style=skia.Paint.kFill_Style,
            Color = skia.Color(255,255,255,255),
            AntiAlias=True)
        rect = skia.Rect.MakeXYWH(0, 0, img.dimensions().fWidth,img.dimensions().fHeight)
        mask.drawRoundRect(rect, corner, corner, paint)
        image_array =  np.bitwise_and(img.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType),mask.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType))
        return skia.Image.fromarray(image_array,colorType=skia.ColorType.kRGBA_8888_ColorType)
        
class BiliMajor:
    def __init__(self, static_path: str, style: PolyStyle) -> None:
        self.src_path = path.join(static_path, "Src")
        self.style = style

    async def run(self, dyn_major: Major, repost: bool = False) -> Optional[np.ndarray]:
        try:
            major_type = dyn_major.type
            if major_type == "MAJOR_TYPE_DRAW":
                return await DynMajorDraw(self.style, dyn_major).run(repost)
            elif major_type == "MAJOR_TYPE_ARCHIVE":
                return await DynMajorArchive(self.src_path,self.style, dyn_major).run(repost)
            else:
                logger.warning(f"{major_type} is not supported")
                return None
        except Exception as e:
            logger.exception(e)
            return None


class DynMajorDraw:
    

    async def run(self, repost: bool) -> Optional[np.ndarray]:
        """
        make image of major draw
        @param repost: bool
        @return:
        """
        try:
            item_count = len(self.major.draw.items)
            background_color = self.style.color.background.repost if repost else self.style.color.background.normal
            if item_count == 1:
                return await self.single_img(background_color, self.major.draw.items)
            elif item_count in {2, 4}:
                return await self.dual_img(background_color, self.major.draw.items)
            else:
                return await self.triplex_img(background_color, self.major.draw.items)
        except Exception:
            logger.exception("Error")
            return None

    async def single_img(self, background_color: str, items) -> np.ndarray:
        src = items[0].src
        img_height = items[0].height
        img_width = items[0].width
        if img_height / img_width > 4:
            img_url = f"{src}@{600}w_{800}h_!header.webp"
        else:
            img_url = src
        img = await get_pictures(img_url)
        if img is not None:
            
            img = img.resize(width=1008, height=int(img.dimensions().height() * 1008 / img.dimensions().width()))
            img_size = img.dimensions()
            surface = skia.Surface(1080, img_size.height() + 20)
            canvas = surface.getCanvas()
            canvas.clear(skia.Color(*background_color))
            await paste(canvas, img, (36, 10))
            return canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

    async def dual_img(self, background_color: str, items):
        url_list = []
        for item in items:
            src = item.src
            img_height = item.height
            img_width = item.width
            if img_height / img_width > 3:
                url_list.append(f"{src}@520w_520h_!header.webp")
            else:
                url_list.append(f"{src}@520w_520h_1e_1c.webp")
        imgs = await get_pictures(url_list, (520, 520))
        num = len(url_list) / 2
        back_size = int(num * 520 + 20 * num)
        surface = skia.Surface(1080, back_size)
        canvas = surface.getCanvas()
        canvas.clear(skia.Color(*background_color))

        x, y = 15, 10
        for i in imgs:
            if i is not None:
                await paste(canvas, i, (x, y))
            x += 530
            if x > 1000:
                x = 15
                y += 530
        return canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

    async def triplex_img(self, background_color: str, items):
        url_list = []
        for item in items:
            src = item.src
            img_height = item.height
            img_width = item.width
            if img_height / img_width > 3:
                url_list.append(f"{src}@260w_260h_!header.webp")
            else:
                url_list.append(f"{src}@260w_260h_1e_1c.webp")
        num = ceil(len(items) / 3)

        imgs = await get_pictures(url_list, (346,346))

        back_size = int(num * 346 + 20 * num)
        surface = skia.Surface(1080, back_size)
        canvas = surface.getCanvas()
        canvas.clear(skia.Color(*background_color))
        x, y = 11, 10
        for img in imgs:
            if img is not None:
                await paste(canvas,img,(x,y))
            x += 356
            if x > 1000:
                x = 11
                y += 356
        return canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
    
class DynMajorArchive(AbstractMajor):
    
    
    async def run(self,repost):
        title = self.major.archive.title
        duration = self.major.archive.duration_text
        badge = self.major.archive.badge
        background_color = self.style.color.background.repost if repost else self.style.color.background.normal
        surface = skia.Surface(1080, 695)
        self.canvas = surface.getCanvas()
        self.canvas.clear(skia.Color(*background_color))
        try:
            cover_img = await get_pictures(f"{self.major.archive.cover}@505w_285h_1c.webp",(1010, 570))
            cover = await self.make_round_cornor(cover_img,20)
            await self.draw_shadow(self.canvas,(35,25,1010,655),20)
            await paste(self.canvas,cover,(35,25))
            tv = skia.Image.open(path.join(self.src_path, "tv.png")).resize(130, 130)
            await paste(self.canvas, tv,(905, 455))
            return self.canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
        except Exception:
            logger.exception("Error")
            return None
        
    
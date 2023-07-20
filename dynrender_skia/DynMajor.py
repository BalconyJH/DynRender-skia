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
import emoji
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
    
    async def draw_text(self,canvas,text:str,font_size,pos:tuple,font_color:tuple):
        paint = skia.Paint(AntiAlias=True, Color=skia.Color(*font_color))
        self.text_font.setSize(font_size)
        self.emoji_font.setSize(font_size)
        text = text.replace("\t","")
        emoji_info = await self.get_emoji_text(text)
        total = len(text) - 1
        x,y,x_bound,y_bound,y_int = pos
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
                offset +=1
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
                y+= y_int
                if y>= y_bound:
                    blob = skia.TextBlob("...", font)
                    canvas.drawTextBlob(blob, x, y-y_int, paint)
                    break
                x = pos[0]
                
        
    async def get_emoji_text(self,text):
        result = emoji.emoji_list(text)
        temp = {}
        for i in result:
            temp[i["match_start"]] = [i["match_end"], i["emoji"]]
        return temp
        
    
    async def draw_shadow(self,canvas,pos:tuple,corner:int,bg_color):
        x,y,width,height= pos
        rec = skia.Rect.MakeXYWH(x,y,width,height)
        paint = skia.Paint(
        Color=skia.Color(*bg_color),
        AntiAlias=True,
        ImageFilter=skia.ImageFilters.DropShadow(0, 0, 10, 10, skia.Color(120,120,120))
        )
        if corner != 0:
            canvas.drawRoundRect(rec, corner, corner, paint)
        else:
            canvas.drawRect(rec,paint)
        
    
    async def make_round_cornor(self,img,corner:int):
        surface = skia.Surface(img.width(),img.height())
        mask = surface.getCanvas()
        paint = skia.Paint(
            Style=skia.Paint.kFill_Style,
            Color = skia.Color(255,255,255,255),
            AntiAlias=True)
        rect = skia.Rect.MakeXYWH(0, 0, img.width(),img.height())
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
    def __init__(self,style,major) -> None:
        self.style = style
        self.major = major
    

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
            
            img = img.resize(width=1008, height=int(img.height() * 1008 / img.width()))
            # img_size = img.dimensions()
            surface = skia.Surface(1080, img.height() + 20)
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
        duration = self.major.archive.duration_text
        background_color = self.style.color.background.repost if repost else self.style.color.background.normal
        surface = skia.Surface(1080, 695)
        self.canvas = surface.getCanvas()
        self.canvas.clear(skia.Color(*background_color))
        tv = skia.Image.open(path.join(self.src_path, "tv.png")).resize(130, 130)
        try:
            cover = await get_pictures(f"{self.major.archive.cover}@505w_285h_1c.webp",(1010, 570))
            duration_img = await self.make_duration(duration)
            await self.draw_shadow(self.canvas,(35,25,1010,655),20,background_color)
            rec = skia.Rect.MakeXYWH(35,25,1010,665)
            self.canvas.clipRRect(skia.RRect(rec,20,20),skia.ClipOp.kIntersect)
            await self.draw_text(self.canvas,self.major.archive.title,self.style.font.font_size.text,(60,650,980,600,10),self.style.color.font_color.text)
            await paste(self.canvas,cover,(35,25))
            await paste(self.canvas, tv,(905, 455))
            await paste(self.canvas,duration_img,(80, 525))
            return self.canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
        except Exception:
            logger.exception("Error")
            return None
        

    async def make_duration(self,duration):
        self.text_font.setSize(self.style.font.font_size.title)
        size = self.text_font.measureText(duration)
        surface = skia.Surface(int(size+20),int(self.text_font.getSize()+20))
        canvas = surface.getCanvas()
        canvas.clear(skia.Color(0, 0, 0, 150))
        blob = skia.TextBlob(duration, self.text_font)
        paint = skia.Paint(AntiAlias=True, Color=skia.Color4f.kWhite)
        canvas.drawTextBlob(blob, 10,int(self.text_font.getSize()+5) , paint)
        duration_img = skia.Image.fromarray(canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType),colorType=skia.ColorType.kRGBA_8888_ColorType)
        return await self.make_round_cornor(duration_img,10)
    
class DynMajorLiveRcmd(AbstractMajor):
    
    async def run(self,repost) -> Optional[np.ndarray]:
        background_color = self.style.color.background.repost if repost else self.style.color.background.normal
        surface = skia.Surface(1080, 695)
        self.canvas = surface.getCanvas()
        self.canvas.clear(skia.Color(*background_color))
        try:
            cover = await get_pictures(f"{self.major.live_rcmd.content.live_play_info.cover}@505w_285h_1c.webp",(1010, 570))
            watch_show = self.major.live_rcmd.content.live_play_info.watched_show.text_large
            watch_show_img = await self.make_watsh_show(watch_show)
            await self.draw_shadow(self.canvas,(35,25,1010,655),20,background_color)
            rec = skia.Rect.MakeXYWH(35,25,1010,665)
            self.canvas.clipRRect(skia.RRect(rec,20,20),skia.ClipOp.kIntersect)
            await self.draw_text(self.canvas,self.major.live_rcmd.content.live_play_info.title,self.style.font.font_size.text,(60,650,980,600,10),self.style.color.font_color.text)
            await paste(self.canvas,cover,(35,25))
            await paste(self.canvas,watch_show_img,(80, 525))
            return self.canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
        except Exception:
            logger.exception("Error")
            return None
        
    async def make_watsh_show(self,watch_show):
        self.text_font.setSize(self.style.font.font_size.title)
        size = self.text_font.measureText(watch_show)
        surface = skia.Surface(int(size+20),int(self.text_font.getSize()+20))
        canvas = surface.getCanvas()
        canvas.clear(skia.Color(0, 0, 0, 150))
        blob = skia.TextBlob(watch_show, self.text_font)
        paint = skia.Paint(AntiAlias=True, Color=skia.Color4f.kWhite)
        canvas.drawTextBlob(blob, 10,int(self.text_font.getSize()+5) , paint)
        watch_show_img = skia.Image.fromarray(canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType),colorType=skia.ColorType.kRGBA_8888_ColorType)
        return await self.make_round_cornor(watch_show_img,10)
    
import asyncio
from os import path
from time import localtime, strftime, time
from typing import Optional

import httpx
import numpy as np
import skia
from dynamicadaptor.Header import Head
from DynConfig import logger
from DynStyle import PolyStyle


class BiliHeader:
    def __init__(self, static_path: str, style: PolyStyle, header_message) -> None:
        self.face_path = path.join(static_path, "Cache", "Face")
        self.emoji_path = path.join(static_path, "Cache", "Emoji")
        self.pendant_path = path.join(static_path, "Cache", "Pendant")
        self.src_path = path.join(static_path, "Src")
        self.style = style
        self.canvas = None
        self.message = None

    async def run(self, header_message: Head) -> Optional[np.ndarray]:
        try:
            self.message = header_message
            surface = skia.Surface(1080, 400)
            self.canvas = surface.getCanvas()
            self.canvas.clear(skia.Color(*self.style.color.backgroud.normal))
            result = await asyncio.gather(self.paste_logo(),
                                 self.draw_name(),
                                 self.draw_pub_time(),
                                 self.get_face_and_pendant(True),
                                 self.get_face_and_pendant()
                                 )
            await self.past_face(result[3])
            await self.paste_pendant(result[4])
            await self.paste_vip()
            
        except Exception:
            logger.exception("Error")
            return None
    
    async def paste_pendant(self,pendant):
        if pendant is not None:
            pendant = pendant.resize(190, 190)
            await self.paste(pendant, (10, 210))
    
    async def paste_vip(self):
        pass
        
    
    async def past_face(self,face):
        face = await self.get_face_and_pendant(True)
        if face:
            face = await self.circle_face(face, 120)
            await self.paste(face,(45,245))
    
    async def get_face_and_pendant(self,img_type:bool=False):
        if img_type:
            img_name = f"{self.message.mid}.webp"
            img_url = f"{self.message.face}@240w_240h_1c_1s.webp"
            img_path = path.join(self.face_path, img_name)
        elif self.message.pendant and self.message.pendant.image:
            img_name = f"{self.message.pendant.pid}.png"
            img_url = f"{self.message.pendant.image}@360w_360h.webp"
            img_path = path.join(self.pendant_path, img_name)
        else:
            return None
        if path.exists(img_path) and (not img_type or time() - int(path.getmtime(img_path)) <= 43200):
            return skia.Image.open(img_path)
        img = await self.get_pictures(img_url)
        if img is not None:
            img.save(img_path)
            return img
        return None

    
    async def get_pictures(self,url):
        try:
            async with httpx.AsyncClient() as client:
                resp = client.get(url)
                assert resp.status_code == 200
            return skia.Image.MakeFromEncoded(resp.content).convert(alphaType=skia.AlphaType.kPremul_AlphaType)
        except Exception:
            return None
    
    async def circle_face(self,img,size):
        surface = skia.Surface(img.dimensions().width(),img.dimensions().height())
        canvas = surface.getCanvas()
        paint = skia.Paint(
            Style=skia.Paint.kFill_Style,
            Color = skia.Color(255,255,255,255),
            AntiAlias=True)
        radius = int(img.dimensions().width()/2)
        canvas.drawCircle(radius,radius,radius,paint)
        paint = skia.Paint(
        Style=skia.Paint.kStroke_Style,
        StrokeWidth=5,
        Color = skia.Color(251, 114, 153),
        AntiAlias=True)
        image_array =  np.bitwise_and(img.toarray(skia.ColorType.kRGBA_8888_ColorType),canvas.toarray())
        surface = skia.Surface(image_array)
        with surface as canvas:
            canvas.drawCircle(radius,radius,radius-2,paint)
        return skia.Image.fromarray(canvas.toarray()).resize(size,size)

    async def draw_pub_time(self):
        if self.message.pub_time:
            pub_time = self.message.pub_time
        elif self.message.pub_ts:
            pub_time = strftime(
                "%Y-%m-%d %H:%M:%S", localtime(self.message.pub_ts))
        else:
            pub_time = time.strftime(
                "%Y-%m-%d %H:%M:%S", localtime(time()))
        
        await self.draw_text(pub_time,
                             self.style.font.font_family,
                             self.style.font.font_style,
                             self.style.color.font_color.sub_title,
                             self.style.font.font_size.time,
                             200, 320)    
    
    async def paste_logo(self) -> None:

        logo = skia.Image.open(path.join(self.src_path, "bilibili.png")).convert(
            alphaType=skia.AlphaType.kPremul_AlphaType).resize(231, 105)
        await self.paste(logo, (433, 20))

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
        await self.draw_text(self.message.name,
                             self.style.font.font_family,
                             self.style.font.font_style,
                             skia.Color(*color),
                             self.style.font.font_size.name,
                             200, 250)

    async def draw_text(self, text, font_family, font_style, font_color, font_size, x, y):
        paint = skia.Paint(AntiAlias=True, Color=font_color)
        font_name = font_family
        offset = x
        for i in text:
            if typeface := skia.FontMgr().matchFamilyStyleCharacter(
                font_family,
                font_style,
                ["zh", "en"],
                ord(i),
            ):
                text_family_name = typeface.getFamilyName()
                if font_name != text_family_name:
                    font_name = text_family_name
                    font = skia.Font(typeface, font_size)
                else:
                    font = skia.Font(None, font_size)
                blob = skia.TextBlob(i, font)
                self.canvas.drawTextBlob(blob, offset, y, paint)
                offset += font.measureText(i)

    async def paste(self, image, position:tuple) -> None:
        x, y = position
        img_height = image.dimensions().fHeight
        img_width = image.dimensions().fWidth
        rec = skia.Rect.MakeXYWH(x, y, img_width, img_height)
        self.canvas.drawImageRect(image, skia.Rect(0, 0, img_width, img_height), rec)

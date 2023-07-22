from .DynTools import DrawText, get_pictures, paste
import skia
from dynamicadaptor.AddonCard import Additional
from typing import Optional
from .DynConfig import PolyStyle
from abc import ABC, abstractmethod
import numpy as np
from os import path
from loguru import logger
import re


class AbstractAdditional(ABC):
    def __init__(self, src_path: str, style: PolyStyle, additional: Additional) -> None:
        self.style = style
        self.additional = additional
        self.src_path = src_path
        self.canvas = None
        self.text_font = skia.Font(skia.Typeface.MakeFromName(self.style.font.font_family, self.style.font.font_style),
                                   self.style.font.font_size.text)
        self.emoji_font = skia.Font(
            skia.Typeface.MakeFromName(self.style.font.emoji_font_family, self.style.font.font_style),
            self.style.font.font_size.text)

    @abstractmethod
    async def run(self, repost: bool) -> Optional[np.ndarray]:
        pass

    async def make_badge(self, badge: str, font_size: int, pos: tuple, img_size: tuple, text_pos: tuple):
        self.text_font.setSize(font_size)
        surface = skia.Surface(*img_size)
        canvas = surface.getCanvas()
        canvas.clear(skia.Color(*self.style.color.font_color.name_big_vip))
        blob = skia.TextBlob(badge, self.text_font)
        paint = skia.Paint(AntiAlias=True, Color=skia.Color4f.kWhite)
        canvas.drawTextBlob(blob, text_pos[0], text_pos[1], paint)
        tag_img = skia.Image.fromarray(canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType),
                                       colorType=skia.ColorType.kRGBA_8888_ColorType)
        tag_img = await self.make_round_cornor(tag_img, 10)
        await paste(self.canvas, tag_img, pos)

    async def make_round_cornor(self, img, corner: int):
        surface = skia.Surface(img.width(), img.height())
        mask = surface.getCanvas()
        paint = skia.Paint(
            Style=skia.Paint.kFill_Style,
            Color=skia.Color(255, 255, 255, 255),
            AntiAlias=True)
        rect = skia.Rect.MakeXYWH(0, 0, img.width(), img.height())
        mask.drawRoundRect(rect, corner, corner, paint)
        image_array = np.bitwise_and(img.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType),
                                     mask.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType))
        return skia.Image.fromarray(image_array, colorType=skia.ColorType.kRGBA_8888_ColorType)

    async def draw_shadow(self, canvas, pos: tuple, corner: int, bg_color):
        x, y, width, height = pos
        rec = skia.Rect.MakeXYWH(x, y, width, height)
        paint = skia.Paint(
            Color=skia.Color(*bg_color),
            AntiAlias=True,
            ImageFilter=skia.ImageFilters.DropShadow(0, 0, 10, 10, skia.Color(120, 120, 120))
        )
        if corner != 0:
            canvas.drawRoundRect(rec, corner, corner, paint)
        else:
            canvas.drawRect(rec, paint)


class BiliAdditional:
    def __init__(self, static_path: str, style: PolyStyle) -> None:
        self.src_path = path.join(static_path, "Src")
        self.style = style

    async def run(self, additional: Additional, repost: bool = False) -> Optional[np.ndarray]:
        additional_type = additional.type
        try:
            if additional_type == "ADDITIONAL_TYPE_RESERVE":
                return await DynAddReserve(self.src_path, self.style, additional).run(repost)
            elif additional_type == "ADDITIONAL_TYPE_UPOWER_LOTTERY":
                return await DynAddUpOwerLottery(self.src_path, self.style, additional).run(repost)
            elif additional_type == "ADDITIONAL_TYPE_GOODS":
                return await DynAddGoods(self.src_path, self.style, additional).run(repost)
            else:
                logger.warning(f"{additional_type} IS NOT SUPPORT NOW")
                return None
        except Exception as e:
            logger.exception(e)
            return None


class DynAddReserve(AbstractAdditional):

    async def run(self, repost) -> Optional[np.ndarray]:
        background_color = self.style.color.background.repost if repost else self.style.color.background.normal
        surface = skia.Surface(1080, 225)
        self.canvas = surface.getCanvas()
        self.canvas.clear(skia.Color(*background_color))
        try:
            await self.draw_shadow(self.canvas, (35, 20, 1010, 185), 15, background_color)
            await self.make_desc()
            await self.make_badge("预约", self.style.font.font_size.text, (850, 75), (170, 75), (45, 50))
            return self.canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
        except Exception as e:
            logger.exception(e)
            return None

    async def make_desc(self):
        draw = DrawText(self.style)
        if self.additional.reserve.desc3 is not None:
            await draw.draw_text(self.canvas, self.additional.reserve.title, self.style.font.font_size.time,
                                 (75, 70, 740, 70, 0), self.style.color.font_color.text)
            desc_1 = f"{self.additional.reserve.desc1.text}  {self.additional.reserve.desc2.text}"
            await draw.draw_text(self.canvas, desc_1, self.style.font.font_size.title,
                                 (75, 120, 810, 120, 0), self.style.color.font_color.sub_title)

            await draw.draw_text(self.canvas, self.additional.reserve.desc3.text, self.style.font.font_size.title,
                                 (105, 170, 810, 170, 0), self.style.color.font_color.rich_text)

            lottery_img = skia.Image.open(path.join(self.src_path, "lottery.png")).resize(40, 40)
            await paste(self.canvas, lottery_img, (65, 138))
        else:
            await draw.draw_text(self.canvas, self.additional.reserve.title, self.style.font.font_size.time,
                                 (75, 100, 740, 100, 0), self.style.color.font_color.text)

            desc_1 = f"{self.additional.reserve.desc1.text}  {self.additional.reserve.desc2.text}"
            await draw.draw_text(self.canvas, desc_1, self.style.font.font_size.title,
                                 (75, 160, 810, 160, 0), self.style.color.font_color.sub_title)


class DynAddUpOwerLottery(AbstractAdditional):

    async def run(self, repost) -> Optional[np.ndarray]:
        background_color = self.style.color.background.repost if repost else self.style.color.background.normal
        surface = skia.Surface(1080, 225)
        self.canvas = surface.getCanvas()
        self.canvas.clear(skia.Color(*background_color))
        try:
            await self.draw_shadow(self.canvas, (35, 20, 1010, 185), 15, background_color)
            await self.make_desc()
            await self.make_badge("去看看", self.style.font.font_size.time, (860, 75), (155, 75), (25, 50))
            return self.canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
        except Exception as e:
            logger.exception(e)
            return None

    async def make_desc(self):
        draw = DrawText(self.style)
        await draw.draw_text(self.canvas, self.additional.upower_lottery.title, self.style.font.font_size.time,
                             (75, 100, 740, 100, 0), self.style.color.font_color.text)

        await draw.draw_text(self.canvas, self.additional.upower_lottery.desc.text, self.style.font.font_size.title,
                             (105, 160, 810, 160, 0), self.style.color.font_color.rich_text)
        lottery_img = skia.Image.open(path.join(self.src_path, "lottery.png")).resize(40, 40)
        await paste(self.canvas, lottery_img, (65, 128))


class DynAddGoods(AbstractAdditional):

    async def run(self, repost):
        background_color = self.style.color.background.repost if repost else self.style.color.background.normal
        surface = skia.Surface(1080, 310)
        self.canvas = surface.getCanvas()
        self.canvas.clear(skia.Color(*background_color))
        try:
            await self.draw_shadow(self.canvas, (35, 50, 1010, 240), 15, background_color)
            await self.make_cover()
            await self.make_title_desc()
            await DrawText(self.style).draw_text(self.canvas, self.additional.goods.head_text,
                                                 self.style.font.font_size.sub_title, (45, 30, 1010, 80, 0),
                                                 self.style.color.font_color.sub_title)
            await self.make_badge("去看看", self.style.font.font_size.time, (860, 125), (155, 75), (25, 50))
            return self.canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
        except Exception as e:
            logger.exception(e)
            return None

    async def make_cover(self):
        url_list = []
        for i in self.additional.goods.items:
            url = re.sub("@(\d+)h_(\d+)w\S+", "", i.cover)
            url_list.append(f"{url}@160w_160h_1c.webp")
        covers = await get_pictures(url_list, (190, 190))
        if len(covers) > 1:
            for i, j in enumerate(covers):
                x = 45 + i * 200
                if x > 1000:
                    break
                await paste(self.canvas, await self.make_round_cornor(j, 10), (x, 75))
        else:
            await paste(self.canvas, await self.make_round_cornor(covers[0], 10), (60, 75))

    async def make_title_desc(self):
        if len(self.additional.goods.items) > 1:
            return
        draw = DrawText(self.style)
        await draw.draw_text(self.canvas, self.additional.goods.items[0].name, self.style.font.font_size.title,
                             (275, 140, 800, 140, 0), self.style.color.font_color.text)

        price = f"{self.additional.goods.items[0].price}起"
        await draw.draw_text(self.canvas, price, self.style.font.font_size.title,
                             (295, 210, 800, 210, 0), self.style.color.font_color.rich_text)


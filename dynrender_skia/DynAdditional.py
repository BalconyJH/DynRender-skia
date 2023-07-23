import re
from abc import ABC, abstractmethod
from os import path
from typing import Optional

import numpy as np
import skia
from dynamicadaptor.AddonCard import Additional
from loguru import logger

from .DynConfig import PolyStyle
from .DynTools import DrawText, get_pictures, paste


class AbstractAdditional(ABC):
    def __init__(self, src_path: str, style: PolyStyle, additional: Additional) -> None:
        self.style = style
        self.additional = additional
        self.src_path = src_path
        self.canvas = None
        self.text_font = skia.Font(skia.Typeface.MakeFromName(self.style.font.font_family, self.style.font.font_style),
                                   self.style.font.font_size.text)
        self.emoji_font = skia.Font(
            skia.Typeface.MakeFromName(
                self.style.font.emoji_font_family, self.style.font.font_style),
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
            ImageFilter=skia.ImageFilters.DropShadow(
                0, 0, 10, 10, skia.Color(120, 120, 120))
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
            elif additional_type == "ADDITIONAL_TYPE_UGC":
                return await DynAddUgc(self.src_path, self.style, additional).run(repost)
            elif additional_type == "ADDITIONAL_TYPE_VOTE":
                return await DynAddVote(self.src_path, self.style, additional).run(repost)
            elif additional_type == "ADDITIONAL_TYPE_COMMON":
                return await DynAddCommon(self.src_path, self.style, additional).run(repost)
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

            lottery_img = skia.Image.open(
                path.join(self.src_path, "lottery.png")).resize(40, 40)
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
        lottery_img = skia.Image.open(
            path.join(self.src_path, "lottery.png")).resize(40, 40)
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
                                                 self.style.font.font_size.sub_title, (
                                                     45, 30, 1010, 80, 0),
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


class DynAddUgc(AbstractAdditional):
    async def run(self, repost):
        background_color = self.style.color.background.repost if repost else self.style.color.background.normal
        surface = skia.Surface(1080, 280)
        self.canvas = surface.getCanvas()
        self.canvas.clear(skia.Color(*background_color))
        try:
            await self.draw_shadow(self.canvas, (35, 20, 1010, 240), 15, background_color)
            rec = skia.Rect.MakeXYWH(35, 20, 1010, 240)
            self.canvas.clipRRect(skia.RRect(rec, 20, 20), skia.ClipOp.kIntersect)
            await self.make_cover()
            await self.make_title_desc()
            await self.make_sub_tag()
            return self.canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
        except Exception as e:
            logger.exception(e)
            return None

    async def make_cover(self):
        cover = await get_pictures(f"{self.additional.ugc.cover}@340w_195h_1c.webp")
        await paste(self.canvas, await self.make_round_cornor(cover, 10), (60, 45))

    async def make_title_desc(self):
        draw = DrawText(self.style)
        await draw.draw_text(self.canvas, self.additional.ugc.title, self.style.font.font_size.title,
                             (430, 90, 990, 140, int(self.style.font.font_size.time * 1.3)),
                             self.style.color.font_color.text)
        await draw.draw_text(self.canvas, self.additional.ugc.desc_second, self.style.font.font_size.title,
                             (430, 220, 950, 220, 0), self.style.color.font_color.sub_title)

    async def make_sub_tag(self):
        self.text_font.setSize(self.style.font.font_size.sub_title)
        size = self.text_font.measureText(self.additional.ugc.duration)
        surface = skia.Surface(int(size + 20), int(self.text_font.getSize() + 20))
        canvas = surface.getCanvas()
        canvas.clear(skia.Color(0, 0, 0, 150))
        blob = skia.TextBlob(self.additional.ugc.duration, self.text_font)
        paint = skia.Paint(AntiAlias=True, Color=skia.Color4f.kWhite)
        canvas.drawTextBlob(blob, 10, int(self.text_font.getSize() + 5), paint)
        sub_tag_img = skia.Image.fromarray(canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType),
                                           colorType=skia.ColorType.kRGBA_8888_ColorType)
        await paste(self.canvas, await self.make_round_cornor(sub_tag_img, 10), (400 - sub_tag_img.width() - 15, 190))


class DynAddVote(AbstractAdditional):

    async def run(self, repost) -> Optional[np.ndarray]:
        background_color = self.style.color.background.repost if repost else self.style.color.background.normal
        surface = skia.Surface(1080, 280)
        self.canvas = surface.getCanvas()
        self.canvas.clear(skia.Color(*background_color))
        try:
            await self.draw_shadow(self.canvas, (35, 20, 1010, 240), 15, background_color)
            rec = skia.Rect.MakeXYWH(35, 20, 1010, 240)
            self.canvas.clipRRect(skia.RRect(rec, 20, 20), skia.ClipOp.kIntersect)
            await self.make_cover()
            await self.make_title_desc()
            await self.make_badge("投票", self.style.font.font_size.time, (860, 95), (155, 75), (42, 50))

            return self.canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
        except Exception as e:
            logger.exception(e)
            return None

    async def make_cover(self):
        cover = skia.Image.open(fp=path.join(self.src_path, "vote_icon.png")).resize(195, 195)
        await paste(self.canvas, await self.make_round_cornor(cover, 10), (60, 45))

    async def make_title_desc(self):
        draw = DrawText(self.style)
        await draw.draw_text(self.canvas, self.additional.vote.desc, self.style.font.font_size.text,
                             (280, 110, 810, 110, 0),
                             self.style.color.font_color.text)
        if self.additional.vote.join_num is None:
            join_num = "0人参与"
        else:
            join_num = f"{self.additional.vote.join_num}人参与"

        await draw.draw_text(self.canvas, join_num, self.style.font.font_size.time,
                             (280, 190, 810, 190, 0), self.style.color.font_color.sub_title)


class DynAddCommon(AbstractAdditional):

    async def run(self, repost) -> Optional[np.ndarray]:
        background_color = self.style.color.background.repost if repost else self.style.color.background.normal
        surface = skia.Surface(1080, 340)
        self.canvas = surface.getCanvas()
        self.canvas.clear(skia.Color(*background_color))
        try:
            await self.draw_shadow(self.canvas, (35, 80, 1010, 245), 15, background_color)

            await DrawText(self.style).draw_text(self.canvas, self.additional.common.head_text,
                                                 self.style.font.font_size.title, (50, 50, 1010, 90, 0),
                                                 self.style.color.font_color.sub_title)

            rec = skia.Rect.MakeXYWH(35, 80, 1010, 240)
            self.canvas.clipRRect(skia.RRect(rec, 20, 20), skia.ClipOp.kIntersect)

            await self.make_cover()
            await self.select_badge()
            await self.select_badge()
            await self.make_title()
            await self.make_desc()

            return self.canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
        except Exception as e:
            logger.exception(e)
            return None

    async def make_cover(self):
        if self.additional.common.sub_type in {'decoration', 'game'}:
            cover_url = f"{self.additional.common.cover}@190w_190h_1c.webp"
            cover = await get_pictures(cover_url, (190, 190))
        else:
            cover_url = f"{self.additional.common.cover}@145w_195h_1c.webp"
            cover = await get_pictures(cover_url, (145, 195))
        await paste(self.canvas, await self.make_round_cornor(cover, 15), (60, 110))

    async def make_title(self):
        if self.additional.common.desc2:
            y = 150
        else:
            y = 180
        if self.additional.common.sub_type in {'decoration', 'game'}:
            x = 280
        else:
            x = 250
        await DrawText(self.style).draw_text(self.canvas, self.additional.common.title, self.style.font.font_size.text,
                                             (x, y, 780, y, 0), self.style.color.font_color.text)

    async def make_desc(self):
        draw = DrawText(self.style)
        if self.additional.common.sub_type in {'decoration', 'game'}:
            x = 280
        else:
            x = 250
        if self.additional.common.desc2:
            await draw.draw_text(self.canvas, self.additional.common.desc1, self.style.font.font_size.title,
                                 (x, 220, 780, 160, 0), self.style.color.font_color.sub_title)

            await draw.draw_text(self.canvas, self.additional.common.desc2, self.style.font.font_size.title,
                                 (x, 285, 780, 225, 0), self.style.color.font_color.sub_title)
        else:
            await draw.draw_text(self.canvas, self.additional.common.desc1, self.style.font.font_size.title,
                                 (x, 250, 780, 190, 0), self.style.color.font_color.sub_title)

    async def select_badge(self):
        badge_text_map = {
            "pugv": "去试看",
            "ogv": "去看看",
            "manga": "去追漫",
            "decoration": "去看看",
            "game": "进入"
        }
        badge_text = badge_text_map.get(self.additional.common.sub_type, "去看看")
        size = self.text_font.measureText(badge_text)
        x = int((155 - size) / 2)
        await self.make_badge(badge_text, self.style.font.font_size.time, (860, 165), (155, 75), (x, 50))

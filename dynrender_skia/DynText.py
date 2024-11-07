# @Time    : 2023/7/15 下午8:12
# @Author  : Polyisoprene
# @File    : DynText.py

import asyncio
from os import path
from typing import Optional

import numpy as np
import skia
from dynamicadaptor.Content import Text
from loguru import logger

from .DynStyle import PolyStyle
from .DynTools import paste, merge_pictures, get_pictures, DrawText


class BiliText:
    """渲染动态的文字部分"""

    def __init__(self, static_path: str, style: PolyStyle) -> None:
        self.emoji_path = path.join(static_path, "Cache", "Emoji")
        self.src_path = path.join(static_path, "Src")
        self.style = style
        surface = skia.Surface(1080, 60)
        self.canvas = surface.getCanvas()
        self.bg_color = None
        self.offset = 40
        self.x_bound = 1030
        self.image_list = []
        self.emoji_dict = {}

    async def run(self, dyn_text: Text, repost: bool = False) -> Optional[np.ndarray]:
        self.text_font = skia.Font(
            skia.Typeface.MakeFromName(self.style.font.font_family, self.style.font.font_style),
            self.style.font.font_size.text,
        )
        self.emoji_font = skia.Font(
            skia.Typeface.MakeFromName(self.style.font.emoji_font_family, self.style.font.font_style),
            self.style.font.font_size.text,
        )
        self.bg_color = self.style.color.background.repost if repost else self.style.color.background.normal
        self.canvas.clear(skia.Color(*self.bg_color))
        try:
            tasks = []
            if dyn_text.topic is not None:
                tasks.append(self.make_topic(dyn_text.topic.name))
            if dyn_text.text:
                tasks.append(self.make_text_image(dyn_text))
            await asyncio.gather(*tasks)
            return await merge_pictures(self.image_list)
        except Exception as e:
            logger.exception(e)
            return None

    async def make_text_image(self, dyn_text):
        emoji_list = []
        emoji_name_list = []
        rich_list = []
        for i in dyn_text.rich_text_nodes:
            if i.type == "RICH_TEXT_NODE_TYPE_EMOJI":
                if i.text not in emoji_name_list:
                    emoji_name_list.append(i.text)
                    emoji_list.append(i.emoji.icon_url)
            elif i.type != "RICH_TEXT_NODE_TYPE_TEXT":
                rich_list.append(i)
        result = await asyncio.gather(self.get_emoji(emoji_list, emoji_name_list), self.get_rich_pic(rich_list))
        await self.draw_text(result[1], dyn_text)  # type: ignore
        if self.offset != 40:
            self.image_list.append(self.canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType))

    async def get_emoji(self, emoji_url: list, emoji_name: list):
        emoji_pic = []
        emoji_index = []
        emoji_url_list = []
        icon_size = int(self.style.font.font_size.text * 1.5)
        for i, emoji_text in enumerate(emoji_name):
            emoji_path = path.join(self.emoji_path, f"{emoji_text}.png")
            if path.exists(emoji_path):
                emoji_pic.append(skia.Image.open(emoji_path))
            else:
                emoji_url_list.append(emoji_url[i])
                emoji_index.append(i)
        if emoji_url_list:
            result = await get_pictures(emoji_url_list, (icon_size, icon_size))
            for i, j in enumerate(emoji_index):
                emoji_path = path.join(self.emoji_path, f"{emoji_name[j]}.png")
                emoji_pic.insert(j, result[i])
                if result[i] is not None:
                    result[i].save(emoji_path)
        temp = {j: emoji_pic[i] for i, j in enumerate(emoji_name)}
        self.emoji_dict = temp

    async def get_rich_pic(self, rich_list):
        rich_dic = {}
        rich_size = self.style.font.font_size.text
        for i in rich_list:
            if i.type == "RICH_TEXT_NODE_TYPE_VOTE":
                if "vote" not in rich_dic:
                    img_path = path.join(self.src_path, "vote.png")
                    img = skia.Image.open(img_path).resize(rich_size, rich_size)
                    rich_dic["vote"] = img
            elif i.type == "RICH_TEXT_NODE_TYPE_LOTTERY":
                if "lottery" not in rich_dic:
                    img_path = path.join(self.src_path, "lottery.png")
                    img = skia.Image.open(img_path).resize(rich_size, rich_size)
                    rich_dic["lottery"] = img
            elif i.type == "RICH_TEXT_NODE_TYPE_GOODS":
                if "goods" not in rich_dic:
                    img_path = path.join(self.src_path, "taobao.png")
                    img = skia.Image.open(img_path).resize(rich_size, rich_size)
                    rich_dic["goods"] = img
            elif i.type in {"RICH_TEXT_NODE_TYPE_WEB", "RICH_TEXT_NODE_TYPE_BV"}:
                if "link" not in rich_dic:
                    img_path = path.join(self.src_path, "link.png")
                    img = skia.Image.open(img_path).resize(rich_size, rich_size)
                    rich_dic["link"] = img
            elif i.type == "RICH_TEXT_NODE_TYPE_CV":
                if "cv" not in rich_dic:
                    img_path = path.join(self.src_path, "article.png")
                    img = skia.Image.open(img_path).resize(rich_size, rich_size)
                    rich_dic["cv"] = img
            elif "link" not in rich_dic:
                img_path = path.join(self.src_path, "link.png")
                img = skia.Image.open(img_path).resize(rich_size, rich_size)
                rich_dic["link"] = img
        return rich_dic

    async def make_topic(self, topic: str) -> None:
        """
        make topic image
        @param topic: topic text
        @return: None
        """
        topic_size = self.style.font.font_size.text
        topic_img = skia.Image.open(path.join(self.src_path, "new_topic.png")).resize(topic_size, topic_size)
        icon_size = int(topic_size * 1.5)
        surface = skia.Surface(1080, icon_size + 10)
        canvas = surface.getCanvas()
        canvas.clear(skia.Color(*self.bg_color))
        await paste(canvas, topic_img, (45, 15))
        await DrawText(self.style).draw_text(
            canvas,
            topic,
            topic_size,
            (45 + topic_size + 10, 50, 1080, 50, 0),
            self.style.color.font_color.rich_text,
        )
        self.image_list.append(canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType))

    async def draw_text(self, rich_list: list, dyn_text: Text):
        self.canvas.clear(skia.Color(*self.bg_color))
        for i in dyn_text.rich_text_nodes:  # type: ignore
            if i.type in {
                "RICH_TEXT_NODE_TYPE_AT",
                "RICH_TEXT_NODE_TYPE_TEXT",
                "RICH_TEXT_NODE_TYPE_TOPIC",
            }:
                if i.type in {"RICH_TEXT_NODE_TYPE_AT", "RICH_TEXT_NODE_TYPE_TOPIC"}:
                    color = skia.Color(*self.style.color.font_color.rich_text)
                else:
                    color = skia.Color(*self.style.color.font_color.text)
                await self.draw_plain_text(i.text, color)
            elif i.type == "RICH_TEXT_NODE_TYPE_EMOJI":
                await self.draw_emoji(i.text)
            else:
                await self.draw_rich_text(i, rich_list)

    async def draw_plain_text(self, dyn_detail, color):
        font = None
        e = False
        dyn_detail = dyn_detail.translate(str.maketrans({"\r": ""}))
        paint = skia.Paint(AntiAlias=True, Color=color)
        emoji_info = await DrawText.get_emoji_text(dyn_detail)
        total = len(dyn_detail) - 1
        offset = 0
        while offset <= total:
            j = dyn_detail[offset]
            if j == "\n":
                self.canvas.saveLayer()
                self.canvas.clear(skia.Color(*self.bg_color))
                self.image_list.append(self.canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType))
                self.canvas.restore()
                offset += 1
                self.offset = 40
                continue
            if offset in emoji_info.keys():
                j = emoji_info[offset][1]
                offset = emoji_info[offset][0]
                font = self.emoji_font
                e = True
            else:
                offset += 1
                font = self.text_font
                e = False
            if font.textToGlyphs(j)[0] == 0:
                if typeface := skia.FontMgr().matchFamilyStyleCharacter(
                    self.style.font.font_family,
                    self.style.font.font_style,
                    ["zh", "en"],
                    ord(j[0]),
                ):
                    font = skia.Font(typeface, self.style.font.font_size.text)
                else:
                    font = self.text_font
            if not e:
                measure = font.measureText(j)
                blob = skia.TextBlob(j, font)
                self.canvas.drawTextBlob(blob, self.offset, 50, paint)
            else:
                measure = font.measureText(j[0])
                blob = skia.TextBlob.MakeFromShapedText(j, font)
                self.canvas.drawTextBlob(blob, self.offset, 5, paint)
            self.offset += measure
            self.offset = await self._handle_boundary_overflow(
                canvas=self.canvas,
                offset=self.offset,
                x_bound=self.x_bound,
                bg_color=self.bg_color,
                image_list=self.image_list,
                reset_offset=40,
            )

    async def draw_emoji(self, emoji_detail):
        img = self.emoji_dict[emoji_detail]
        if img is not None:
            img_size = img.dimensions().width()
            await paste(self.canvas, img, (int(self.offset), 0))
            self.offset += img_size + 5
            self.offset = await self._handle_boundary_overflow(
                canvas=self.canvas,
                offset=self.offset,
                x_bound=self.x_bound,
                bg_color=self.bg_color,
                image_list=self.image_list,
                reset_offset=40,
            )

    async def draw_rich_text(self, text_detail, rich_list):
        if text_detail.type == "RICH_TEXT_NODE_TYPE_VOTE":
            icon = rich_list["vote"]
        elif text_detail.type == "RICH_TEXT_NODE_TYPE_LOTTERY":
            icon = rich_list["lottery"]
        elif text_detail.type == "RICH_TEXT_NODE_TYPE_GOODS":
            icon = rich_list["goods"]
        elif text_detail.type == "RICH_TEXT_NODE_TYPE_CV":
            icon = rich_list["cv"]
        else:
            icon = rich_list["link"]
        await paste(
            self.canvas,
            icon,
            (int(self.offset), int(60 - icon.dimensions().height()) / 2),
        )
        self.offset += icon.dimensions().width() + 5
        if self.offset >= self.x_bound:
            self.canvas.saveLayer()
            self.canvas.clear(skia.Color(*self.bg_color))
            self.image_list.append(self.canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType))
            self.canvas.restore()
            self.offset = 40
        paint = skia.Paint(AntiAlias=True, Color=skia.Color(*self.style.color.font_color.rich_text))
        font = self.text_font
        for i in text_detail.text:
            if font.textToGlyphs(i)[0] == 0:
                if typeface := skia.FontMgr().matchFamilyStyleCharacter(
                    self.style.font.font_family,
                    self.style.font.font_style,
                    ["zh", "en"],
                    ord(i),
                ):
                    font = skia.Font(typeface, self.style.font.font_size.text)
                else:
                    font = self.text_font
            blob = skia.TextBlob(i, font)
            self.canvas.drawTextBlob(blob, self.offset, 50, paint)
            self.offset += font.measureText(i)
            self.offset = await self._handle_boundary_overflow(
                canvas=self.canvas,
                offset=self.offset,
                x_bound=self.x_bound,
                bg_color=self.bg_color,
                image_list=self.image_list,
                reset_offset=40,
            )

    @staticmethod
    async def _handle_boundary_overflow(
        canvas: skia.Canvas,
        offset: int,
        x_bound: int,
        bg_color: tuple[int, int, int, int],
        image_list: list,
        reset_offset: int = 40,
    ) -> int:
        """
        Handles the logic when the drawing position exceeds the specified width boundary.

        This method checks if the current drawing offset exceeds the x-axis boundary (`x_bound`).
        If it does, the method saves the current canvas layer, clears it with the specified
        background color (`bg_color`), appends the current canvas content to `image_list`,
        and restores the canvas. It then resets the drawing offset to a specified value (`reset_offset`).

        Args:
            canvas (skia.Canvas): The canvas object where drawing operations are performed.
            offset (int): The current drawing offset along the x-axis.
            x_bound (int): The maximum width boundary for drawing before a reset is needed.
            bg_color (tuple[int, int, int, int]): The background color (RGBA) used to clear the canvas.
            image_list (list): A list to store each canvas layer as an image array.
            reset_offset (int, optional): The x-axis offset reset value after exceeding the boundary. Defaults to 40.

        Usage:
        ```python
        offset = await self._handle_boundary_overflow(canvas, offset, x_bound, bg_color, image_list, reset_offset)
        ```

        Returns:
            int: The updated offset value, either the reset offset or the original offset if within bounds.
        """
        if offset >= x_bound:
            canvas.saveLayer()
            canvas.clear(skia.Color(*bg_color))
            image_list.append(canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType))
            canvas.restore()
            return reset_offset
        return offset

# -*- coding: utf-8 -*-
# @Time    : 2023/7/15 下午8:12
# @Author  : Polyisoprene
# @File    : DynText.py

from os import path

import emoji
import skia
import asyncio
import numpy as np
from typing import Optional
from loguru import logger
from .DynStyle import PolyStyle
from .DynTools import paste, merge_pictures, get_pictures
from dynamicadaptor.Content import Text


class BiliText:
    """渲染动态的文字部分"""

    def __init__(self, static_path: str, style: PolyStyle) -> None:
        self.emoji_path = path.join(static_path, "Cache", "Emoji")
        self.src_path = path.join(static_path, "Src")
        self.style = style
        surface = skia.Surface(1080, 60)
        self.canvas = surface.getCanvas()
        self.offset = 40
        self.x_bound = 1040
        self.image_list = []
        self.emoji_dict = {}

    async def run(self, dyn_text: Text, repost: bool = False) -> Optional[np.ndarray]:
        background_color = self.style.color.background.repost if repost else self.style.color.background.normal
        self.canvas.clear(skia.Color(*background_color))
        try:
            tasks = []
            if dyn_text.topic is not None:
                tasks.append(self.make_topic(dyn_text.topic.name, repost))
            if dyn_text.text:
                tasks.append(self.make_text_image(dyn_text, repost))
            await asyncio.gather(*tasks)
            return await merge_pictures(self.image_list)
        except Exception as e:
            logger.exception("Error")
            return None

    async def make_text_image(self, dyn_text, repost: bool):
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
        await self.draw_text(result[1], dyn_text)

    async def get_emoji(self, emoji_url: list, emoji_name: list):
        emoji_pic = []
        emoji_index = []
        emoji_url_list = []
        temp = {}
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
                result[i].save(emoji_path)
        for i, j in enumerate(emoji_name):
            temp[j] = emoji_pic[i]
        self.emoji_dict = temp

    async def get_emoji_text(self, text: str):
        result = emoji.emoji_list(text)
        temp = {}
        for i in result:
            temp[i["match_start"]] = [i["match_end"], i["emoji"]]
        return temp

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
            else:
                if "link" not in rich_dic:
                    img_path = path.join(self.src_path, "link.png")
                    img = skia.Image.open(img_path).resize(rich_size, rich_size)
                    rich_dic["link"] = img
        return rich_dic

    async def make_topic(self, topic: str, repost: bool) -> None:
        """
        make topic image
        @param topic: topic text
        @param repost: Is the text within the forwarded content
        @return: None
        """
        topic_size = self.style.font.font_size.text
        topic_img = skia.Image.open(path.join(self.src_path, "new_topic.png")).resize(topic_size, topic_size)
        icon_size = int(topic_size * 1.5)
        surface = skia.Surface(1080, icon_size + 10)
        canvas = surface.getCanvas()
        background_color = self.style.color.background.repost if repost else self.style.color.background.normal
        canvas.clear(skia.Color(*background_color))
        await paste(canvas, topic_img, (45, 15))

        paint = skia.Paint(AntiAlias=True, Color=skia.Color(*self.style.color.font_color.rich_text))
        font_name = None
        offset = 45 + topic_size + 10
        font = None
        for i in topic:
            if typeface := skia.FontMgr().matchFamilyStyleCharacter(
                    self.style.font.font_family,
                    self.style.font.font_style,
                    ["zh", "en"],
                    ord(i),
            ):
                text_family_name = typeface.getFamilyName()
                if font_name != text_family_name:
                    font_name = text_family_name
                    font = skia.Font(typeface, topic_size)
            else:
                font = skia.Font(None, topic_size)
            blob = skia.TextBlob(i, font)
            canvas.drawTextBlob(blob, offset, 50, paint)
            offset += font.measureText(i)
        self.image_list.append(canvas.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType))

    async def draw_text(self, text: str, color: tuple, repost: bool):
        pass

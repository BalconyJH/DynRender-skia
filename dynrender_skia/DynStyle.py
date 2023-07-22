# -*- coding: utf-8 -*-
'''
@File    :   DynStyle.py
@Time    :   2023/07/16 20:42:46
@Author  :   Polyisoprene
@Version :   1.0
@Desc    :   None
'''

from typing import Any

from pydantic import BaseModel


class FontSize(BaseModel):
    text: int
    name: int
    time: int
    title: int
    sub_title: int


class FontColor(BaseModel):
    text: tuple
    title: tuple
    name_big_vip: tuple
    name_small_vip: tuple
    rich_text: tuple
    sub_title: tuple
    white: tuple


class BackgroundColor(BaseModel):
    normal: tuple
    repost: tuple
    border: tuple


class FontCfg(BaseModel):
    font_family: str
    emoji_font_family: str
    font_style: Any
    font_size: FontSize


class ColorCfg(BaseModel):
    font_color: FontColor
    background: BackgroundColor


class PolyStyle(BaseModel):
    font: FontCfg
    color: ColorCfg

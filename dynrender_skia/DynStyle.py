# -*- coding: utf-8 -*-
"""
@File    :   DynStyle.py
@Time    :   2023/07/16 20:42:46
@Author  :   Polyisoprene
@Version :   1.0
@Desc    :   None
"""

from pathlib import Path
from typing import Any, Union

from pydantic import BaseModel, validator


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

    @validator("font_family", "emoji_font_family", always=True, pre=True)
    def _change_path_to_str(cls, v: Union[str, Path]):
        v_ = Path(v)
        if v_.exists() and v_.is_file():
            return v_.as_posix()
        else:
            return v


class ColorCfg(BaseModel):
    font_color: FontColor
    background: BackgroundColor


class PolyStyle(BaseModel):
    font: FontCfg
    color: ColorCfg

from pydantic import BaseModel
from typing import Any

class FontSize(BaseModel):
    text:int
    name:int
    time:int
    title:int
    sub_title:int
    
    
class FontColor(BaseModel):
    text:tuple
    title:tuple
    name_big_vip:tuple
    name_small_vip:tuple
    rich_text:tuple
    sub_title:tuple
    white:tuple
    

class BackgroudColor(BaseModel):
    normal:tuple
    repost:tuple
    border:tuple
    
class FontCfg(BaseModel):
    font_family:str
    font_style:Any
    font_size:FontSize


class ColorCfg(BaseModel):
    font_color:FontColor
    backgroud:BackgroudColor

class PolyStyle(BaseModel):
    font:FontCfg
    color:ColorCfg
    

    

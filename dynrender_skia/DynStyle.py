from pydantic import BaseModel
from typing import Any,Tuple

class FontSize(BaseModel):
    text:int
    name:int
    time:int
    title:int
    sub_title:int
    
    
class FontColor(BaseModel):
    text:Tuple[float,float,float,float]
    name:Tuple[float,float,float,float]
    time:Tuple[float,float,float,float]
    name_big_vip:Tuple[float,float,float,float]
    name_small_vip:Tuple[float,float,float,float]
    rich_text:Tuple[float,float,float,float]
    background:Tuple[float,float,float,float]
    sub_title:Tuple[float,float,float,float]
    white:Tuple[float,float,float,float]
    

class BackgroudColor(BaseModel):
    normal:Tuple[float,float,float,float]
    repost:Tuple[float,float,float,float]

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
    

    

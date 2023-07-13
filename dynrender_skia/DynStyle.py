from pydantic import BaseModel
from typing import Any,Tuple
import skia

class FontSize(BaseModel):
    text:Tuple[float,float,float,float]
    name:Tuple[float,float,float,float]
    time:Tuple[float,float,float,float]
    name_big_vip:Tuple[float,float,float,float]
    name_small_vip:Tuple[float,float,float,float]
    rich_text:Tuple[float,float,float,float]
    background:Tuple[float,float,float,float]
    sub_title:Tuple[float,float,float,float]
    
    


class FontCfg(BaseModel):
    font_family:str
    font_style:Any
    font_size:FontSize



class PolyStyle(BaseModel):
    font:FontCfg
    

    

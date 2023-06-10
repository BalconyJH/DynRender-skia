from pydantic import BaseModel
from typing import Tuple, Union


class Size(BaseModel):
    height: Union[None, float, int]
    width: Union[None, float, int]


class Coordinate(BaseModel):
    x: int
    y: int


class Info(BaseModel):
    size: Size
    coordinate: Coordinate
    hidden: bool


class textInfo(BaseModel):
    coordinate: Coordinate
    fontSize: int


class Header(BaseModel):
    bk_size: Size
    cover: Info
    pendant: Info
    vip: Info
    name: textInfo
    time: textInfo

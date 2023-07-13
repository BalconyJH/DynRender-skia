#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   DynConfig.py
@Time    :   2023/07/13 14:20:02
@Author  :   Polyisoprene 
@Version :   1.0
@Desc    :   None
"""


from os import path, getcwd, makedirs
from loguru import logger
from typing import Optional
from zipfile import ZipFile
try:
    import skia
except ImportError as e:
    logger.error(e)
    logger.warning(
        "please install dependence: \n\n Ubuntu: apt install libgl1-mesa-glx \n\n ArchLinux: pacman -S libgl \n\n Centos: yum install mesa-libGL -y")
from .DynStyle import PolyStyle


class MakeStaticFile:
    def __init__(self, data_path: Optional[str] = None) -> None:
        self.data_path: str = data_path

    @property
    def check_cache_file(self) -> None:
        """查询缓存文件是否存在"""
        # 查询是否有data_path参数
        # 没有的话静态文件目录就设置在程序的运行目录
        # 当前文件所在的目录的路径
        current_dir = path.dirname(path.abspath(__file__))
        if self.data_path is None:
            # 确定程序的运行目录的路径
            program_running_path = getcwd()
            # 静态文件的路径
            static_path = path.join(program_running_path, "Static")
            # 如果不存在静态目录将自带的压缩文件解压过去
            if not path.exists(static_path):
                logger.info("未检测到static目录")
                file = self.unzip_file(
                    "用户未传入data路径,将在程序运行目录创建static目录", "创建static目录中...", current_dir
                )
                file.extractall(program_running_path)
                logger.info("static目录创建成功")
        else:
            # 设置静态文件的目录
            static_path = path.join(self.data_path, "Static")
            if not path.exists(self.data_path):
                # 如果data_path不存在创建这个目录
                makedirs(self.data_path)
            if not path.exists(static_path):
                file = self.unzip_file(
                    "未检测到static目录", "使用用户传入路径创建static目录中...", current_dir
                )
                file.extractall(self.data_path)
                logger.info("static目录创建成功")
        return static_path

    def unzip_file(self, arg0, arg1, current_dir):
        logger.info(arg0)
        logger.info(arg1)
        return ZipFile(path.join(current_dir, "Static.zip"))


class SetDynStyle:
    def __init__(self, font_family: str, font_style: str) -> None:
        self.font_family = font_family
        self.font_style = font_style

    def set_style(self):
        
        cfg = PolyStyle()
        cfg.font.font_family = self.font_family
        cfg.font.font_style = self.get_font_style()
        

    def get_font_style(self):
        style_map = {"Normal": skia.FontStyle().Normal(), "Bold": skia.FontStyle().Bold(
        ), "Italic": skia.FontStyle().Italic(), "BoldItalic": skia.FontStyle().BoldItalic()}
        return style_map.get(self.font_style, skia.FontStyle().Normal())

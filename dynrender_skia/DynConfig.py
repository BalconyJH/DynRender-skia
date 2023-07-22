# -*- coding: utf-8 -*-
"""
@File    :   DynConfig.py
@Time    :   2023/07/13 14:20:02
@Author  :   Polyisoprene 
@Version :   1.0
@Desc    :   None
"""
import json
from os import getcwd, makedirs, path
from typing import Optional
from zipfile import ZipFile

from loguru import logger

try:
    import skia
except ImportError as e:
    logger.error(e)
    logger.warning(
        "Missing dependent files \n\n please install dependence: \n\n ---------------------------------------\n\n "
        "Ubuntu: apt install libgl1-mesa-glx \n\n ArchLinux: pacman -S libgl \n\n Centos: yum install mesa-libGL -y "
        "\n\n---------------------------------------")
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
                self.unzip_file(
                    "用户未传入data路径,将在程序运行目录创建static目录",
                    "创建static目录中...",
                    current_dir,
                    program_running_path
                )
                logger.info("static目录创建成功")
        else:
            # 设置静态文件的目录
            static_path = path.join(self.data_path, "Static")
            if not path.exists(self.data_path):
                # 如果data_path不存在创建这个目录
                makedirs(self.data_path)
            if not path.exists(static_path):
                self.unzip_file(
                    "未检测到static目录",
                    "使用用户传入路径创建static目录中...",
                    current_dir,
                    self.data_path
                )
                logger.info("static目录创建成功")
        font_cache_path = path.join(static_path, "font_family.json")
        if not path.exists(font_cache_path):
            logger.info("创建系统安装的所有字体的名称列表文件")
            font_list = list(skia.FontMgr())
            with open(font_cache_path, "w") as f:
                f.write(json.dumps(font_list, ensure_ascii=False))
            logger.info("字体列表文件创建完成")
            logger.info(f"文件存储于：{font_cache_path}")
        else:
            new_font_list = list(skia.FontMgr())
            with open(font_cache_path, "w+") as f:
                if file_content := f.read():
                    old_font_list = json.loads(file_content)
                    if new_font_list != old_font_list:
                        f.write(json.dumps(new_font_list, ensure_ascii=False))
                else:
                    f.write(json.dumps(new_font_list, ensure_ascii=False))

        return static_path

    def unzip_file(self, arg0, arg1, src_path, target_path):
        logger.info(arg0)
        logger.info(arg1)
        file = ZipFile(path.join(src_path, "Static.zip"))
        file.extractall(target_path)


class SetDynStyle:
    def __init__(self, font_family: str, emoji_font_family: str, font_style: str) -> None:
        self.font_family = font_family
        self.font_style = font_style
        self.emoji_font_family = emoji_font_family

    @property
    def set_style(self) -> PolyStyle:
        cfg_obj = {
            "color": {
                "font_color": {
                    "text": (0, 0, 0, 255),
                    "sub_title": (153, 162, 170, 255),
                    "title": (0, 0, 0, 255),
                    "name_big_vip": (251, 107, 148, 255),
                    "name_small_vip": (60, 232, 78, 255),
                    "rich_text": (0, 161, 214, 255),
                    "white": (255, 255, 255, 255)
                },
                "background": {
                    "normal": (255, 255, 255, 255),
                    "repost": (241, 242, 243, 255),
                    "border": (229, 233, 239, 255)
                }

            },
            "font": {
                "font_family": self.font_family,
                "emoji_font_family": self.emoji_font_family,
                "font_style": self.get_font_style(),
                "font_size": {
                    "name": 45,
                    "text": 40,
                    "time": 35,
                    "title": 30,
                    "sub_title": 20
                }
            }
        }

        return PolyStyle(**cfg_obj)

    def get_font_style(self):
        style_map = {"Normal": skia.FontStyle().Normal(), "Bold": skia.FontStyle().Bold(
        ), "Italic": skia.FontStyle().Italic(), "BoldItalic": skia.FontStyle().BoldItalic()}
        return style_map.get(self.font_style, skia.FontStyle().Normal())

# if __name__ == "__main__":
#     a = SetDynStyle("Noto Sans CJK SC","Normal").set_style
#     print(a.color.backgroud.repost)

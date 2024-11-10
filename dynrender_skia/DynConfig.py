import json
from collections.abc import Iterable
from os import getcwd, path
from typing import Optional, cast
from zipfile import ZipFile, BadZipFile

import skia
from loguru import logger

from .DynStyle import PolyStyle


class MakeStaticFile:
    def __init__(self, data_path: Optional[str] = None) -> None:
        self.data_path: Optional[str] = data_path

    @property
    def check_cache_file(self) -> str:
        """Check if the cache file exists, creating necessary directories if needed."""
        if self.data_path is None:
            program_running_path = getcwd()
            logger.info("No path provided; creating static directory in the program directory.")
            static_path = self._ensure_static_directory(program_running_path)
        else:
            logger.info("Path provided; creating static directory in the provided path.")
            static_path = self._ensure_static_directory(self.data_path)

        font_cache_path = path.join(static_path, "font_family.json")
        self._create_or_update_font_cache(font_cache_path)

        return static_path

    def _ensure_static_directory(self, base_path: str) -> str:
        """
        Ensures the existence of a 'Static' directory at the specified base_path.
        If the directory does not exist, it unzips the necessary files into it.
        """
        static_path = path.join(base_path, "Static")
        if not path.exists(static_path):
            logger.info("Static directory not detected.")
            current_dir = path.dirname(path.abspath(__file__))
            self.unzip_file(
                current_dir,
                base_path,
            )
            logger.info("Static directory successfully created.")
        return static_path

    @staticmethod
    def _create_or_update_font_cache(font_cache_path: str) -> None:
        """
        Creates or updates a JSON file listing all installed fonts on the system.
        """
        font_mgr = skia.FontMgr()
        font_list = list(cast(Iterable[str], font_mgr))
        logger.debug(f"Font list: {font_list}")

        if not path.exists(font_cache_path):
            with open(font_cache_path, "w", encoding="utf-8") as f:
                json.dump(font_list, f, ensure_ascii=False)
            logger.info(f"Font list cache saved at: {font_cache_path}")
        else:
            logger.debug(f"Font list cache already exists at: {font_cache_path}")
            with open(font_cache_path, "r+", encoding="utf-8") as f:
                if file_content := f.read():
                    old_font_list = json.loads(file_content)
                    if font_list != old_font_list:
                        f.seek(0)
                        json.dump(font_list, f, ensure_ascii=False)
                        f.truncate()  # Truncate the file to the current position
                        logger.info("Font list cache updated successfully.")

                else:
                    json.dump(font_list, f, ensure_ascii=False)
                    logger.info("Font list cache created successfully.")

    @staticmethod
    def unzip_file(src_path: str, target_path: str) -> None:
        """
        Extracts the contents of a ZIP file located in the specified source path to the target path.

        Args:
            src_path (str): The directory path where the ZIP file ("Static.zip") is located.
            target_path (str): The directory path where the contents of the ZIP file will be extracted.

        Returns:
            None

        Raises:
            FileNotFoundError: If the ZIP file does not exist at the specified source path.
            BadZipFile: If the ZIP file is corrupt or unreadable.
            PermissionError: If there are permission issues while accessing the paths.
        """
        zip_file_path = path.join(src_path, "Static.zip")

        try:
            if not path.isfile(zip_file_path):
                logger.error(f"ZIP file not found at path: {zip_file_path}")
                raise FileNotFoundError(f"ZIP file not found at path: {zip_file_path}")

            with ZipFile(zip_file_path, "r") as zip_file:
                zip_file.extractall(target_path)
                logger.info(f"Successfully extracted ZIP file to {target_path}")

        except BadZipFile:
            logger.error(f"Bad ZIP file or corrupt file at path: {zip_file_path}")
            raise
        except PermissionError as e:
            logger.error(f"Permission denied while accessing {zip_file_path} or {target_path}: {e}")
            raise
        except Exception as e:
            logger.exception(f"An unexpected error occurred during extraction: {e}")
            raise


class SetDynStyle:
    """
    Set the style of the dynamic rendering.

    Args:
        font_family (str): Font family name like "Noto Sans CJK SC".
        emoji_font_family (str): Emoji font family name like "Noto Color Emoji".
        font_style (str): Font style like "Normal、Bold、Italic、BoldItalic".

    Returns:
        PolyStyle: A Pydantic model containing the font and color configurations.
    """

    def __init__(self, font_family: str, emoji_font_family: str, font_style: str) -> None:
        self.font_family = font_family
        self.font_style = font_style
        self.emoji_font_family = emoji_font_family

    @property
    def set_style(self) -> PolyStyle:
        """
        Set the style of the dynamic rendering.

        Returns:
            PolyStyle: A Pydantic model containing the font and color configurations.
        """
        cfg_obj = {
            "color": {
                "font_color": {
                    "text": (0, 0, 0, 255),
                    "sub_title": (153, 162, 170, 255),
                    "title": (0, 0, 0, 255),
                    "name_big_vip": (251, 107, 148, 255),
                    "name_small_vip": (60, 232, 78, 255),
                    "rich_text": (0, 161, 214, 255),
                    "white": (255, 255, 255, 255),
                },
                "background": {
                    "normal": (255, 255, 255, 255),
                    "repost": (241, 242, 243, 255),
                    "border": (229, 233, 239, 255),
                },
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
                    "sub_title": 20,
                },
            },
        }

        return PolyStyle(**cfg_obj)

    def get_font_style(self) -> skia.FontStyle:
        """
        Returns the skia.FontStyle object based on the font style string.

        Returns:
            skia.FontStyle: The skia.FontStyle object corresponding to the font style string
        """
        style_map = {
            "Normal": skia.FontStyle().Normal(),
            "Bold": skia.FontStyle().Bold(),
            "Italic": skia.FontStyle().Italic(),
            "BoldItalic": skia.FontStyle().BoldItalic(),
        }
        return style_map.get(self.font_style, skia.FontStyle().Normal())

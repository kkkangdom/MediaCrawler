# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/store/zhihu/zhihu_store_media.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#

# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

# @Desc    : Zhihu media storage
import pathlib
from typing import Dict
from urllib.parse import urlparse

import aiofiles

from base.base_crawler import AbstractStoreImage, AbstractStoreVideo
from tools import utils
import config


def _guess_extension(url: str, default_ext: str) -> str:
    if not url:
        return default_ext
    path = urlparse(url).path
    if "." in path:
        ext = path.split(".")[-1]
        if ext:
            return ext.split("/")[0]
    return default_ext


class ZhihuImageStore(AbstractStoreImage):
    def __init__(self):
        if config.SAVE_DATA_PATH:
            self.image_store_path = f"{config.SAVE_DATA_PATH}/zhihu/images"
        else:
            self.image_store_path = "data/zhihu/images"

    async def store_image(self, image_content_item: Dict):
        await self.save_image(
            image_content_item.get("content_id"),
            image_content_item.get("index"),
            image_content_item.get("pic_content"),
            image_content_item.get("url"),
        )

    def make_save_file_name(self, content_id: str, index: int, extension_file_name: str) -> str:
        return f"{self.image_store_path}/{content_id}/{index}.{extension_file_name}"

    async def save_image(self, content_id: str, index: int, pic_content: bytes, url: str):
        if not content_id or pic_content is None:
            return
        pathlib.Path(f"{self.image_store_path}/{content_id}").mkdir(parents=True, exist_ok=True)
        extension = _guess_extension(url, "jpg")
        save_file_name = self.make_save_file_name(content_id, index, extension)
        async with aiofiles.open(save_file_name, "wb") as f:
            await f.write(pic_content)
            utils.logger.info(f"[ZhihuImageStore.save_image] save image {save_file_name} success ...")


class ZhihuVideoStore(AbstractStoreVideo):
    def __init__(self):
        if config.SAVE_DATA_PATH:
            self.video_store_path = f"{config.SAVE_DATA_PATH}/zhihu/videos"
        else:
            self.video_store_path = "data/zhihu/videos"

    async def store_video(self, video_content_item: Dict):
        await self.save_video(
            video_content_item.get("content_id"),
            video_content_item.get("index"),
            video_content_item.get("video_content"),
            video_content_item.get("url"),
        )

    def make_save_file_name(self, content_id: str, index: int, extension_file_name: str) -> str:
        return f"{self.video_store_path}/{content_id}/{index}.{extension_file_name}"

    async def save_video(self, content_id: str, index: int, video_content: bytes, url: str):
        if not content_id or video_content is None:
            return
        pathlib.Path(f"{self.video_store_path}/{content_id}").mkdir(parents=True, exist_ok=True)
        extension = _guess_extension(url, "mp4")
        save_file_name = self.make_save_file_name(content_id, index, extension)
        async with aiofiles.open(save_file_name, "wb") as f:
            await f.write(video_content)
            utils.logger.info(f"[ZhihuVideoStore.save_video] save video {save_file_name} success ...")

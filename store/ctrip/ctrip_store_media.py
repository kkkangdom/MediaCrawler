# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler
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

import pathlib
from typing import Dict

import aiofiles

from base.base_crawler import AbstractStoreImage, AbstractStoreVideo
from tools import utils
import config


class CtripStoreImage(AbstractStoreImage):
    def __init__(self):
        if config.SAVE_DATA_PATH:
            self.image_store_path = f"{config.SAVE_DATA_PATH}/ctrip/images"
        else:
            self.image_store_path = "data/ctrip/images"

    async def store_image(self, image_content_item: Dict):
        """Store image"""
        await self.save_image(
            image_content_item.get("pic_id"),
            image_content_item.get("pic_content"),
            image_content_item.get("extension_file_name", "jpg")
        )

    def make_save_file_name(self, pic_id: str, extension_file_name: str) -> str:
        """Make save file name"""
        return f"{self.image_store_path}/{pic_id}.{extension_file_name}"

    async def save_image(self, pic_id: str, pic_content: bytes, extension_file_name: str = "jpg"):
        """Save image to local"""
        pathlib.Path(self.image_store_path).mkdir(parents=True, exist_ok=True)
        save_file_name = self.make_save_file_name(pic_id, extension_file_name)
        async with aiofiles.open(save_file_name, 'wb') as f:
            await f.write(pic_content)
            utils.logger.info(f"[CtripStoreImage.save_image] save image {save_file_name} success")


class CtripStoreVideo(AbstractStoreVideo):
    def __init__(self):
        if config.SAVE_DATA_PATH:
            self.video_store_path = f"{config.SAVE_DATA_PATH}/ctrip/videos"
        else:
            self.video_store_path = "data/ctrip/videos"

    async def store_video(self, video_content_item: Dict):
        """Store video"""
        await self.save_video(
            video_content_item.get("video_id"),
            video_content_item.get("video_content"),
            video_content_item.get("extension_file_name", "mp4")
        )

    def make_save_file_name(self, video_id: str, extension_file_name: str) -> str:
        """Make save file name"""
        return f"{self.video_store_path}/{video_id}.{extension_file_name}"

    async def save_video(self, video_id: str, video_content: bytes, extension_file_name: str = "mp4"):
        """Save video to local"""
        pathlib.Path(self.video_store_path).mkdir(parents=True, exist_ok=True)
        save_file_name = self.make_save_file_name(video_id, extension_file_name)
        async with aiofiles.open(save_file_name, 'wb') as f:
            await f.write(video_content)
            utils.logger.info(f"[CtripStoreVideo.save_video] save video {save_file_name} success")

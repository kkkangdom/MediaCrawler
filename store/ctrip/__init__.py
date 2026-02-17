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

import json
import pathlib
from typing import Dict, List
import aiofiles

from model.m_ctrip import CtripReview, CtripComment
from tools import utils
from var import source_keyword_var, crawler_type_var
import config

from .ctrip_store_media import CtripStoreImage, CtripStoreVideo


# In-memory storage for reviews
_reviews_data: List[Dict] = []


class CtripStoreFactory:
    """Factory for creating Ctrip store instances"""
    
    @staticmethod
    async def save_review(review: CtripReview) -> None:
        """Save review to in-memory storage"""
        review_dict = review.dict()
        _reviews_data.append(review_dict)
        utils.logger.info(f"[CtripStoreFactory.save_review] Saved review {review.review_id}")

    @staticmethod
    async def save_data_to_file() -> None:
        """Save all reviews to file"""
        if not _reviews_data:
            utils.logger.info("[CtripStoreFactory.save_data_to_file] No reviews to save")
            return
        
        if config.SAVE_DATA_OPTION == "json":
            await CtripStoreFactory._save_to_json()
        elif config.SAVE_DATA_OPTION == "excel":
            await CtripStoreFactory._save_to_excel()
        # Support other formats as needed

    @staticmethod
    async def _save_to_json() -> None:
        """Save reviews to JSON file"""
        file_path = f"data/ctrip/{source_keyword_var.get()}_reviews.json"
        pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(_reviews_data, ensure_ascii=False, indent=2))
            utils.logger.info(f"[CtripStoreFactory._save_to_json] Saved {len(_reviews_data)} reviews to {file_path}")

    @staticmethod
    async def _save_to_excel() -> None:
        """Save reviews to Excel file"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill
        except ImportError:
            utils.logger.error("[CtripStoreFactory._save_to_excel] openpyxl not installed")
            return
        
        file_path = f"data/ctrip/{source_keyword_var.get()}_reviews.xlsx"
        pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Reviews"
        
        # Write headers
        headers = ["Review ID", "Title", "Content", "Author", "Location", "Created Time", "Views", "Likes", "Replies", "Images", "Videos"]
        ws.append(headers)
        
        # Style headers
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
        
        # Write data
        for review in _reviews_data:
            ws.append([
                review.get("review_id", ""),
                review.get("title", ""),
                review.get("content", "")[:100],  # Truncate content
                review.get("user_nickname", ""),
                review.get("poi_name", ""),
                review.get("created_time", ""),
                review.get("view_count", 0),
                review.get("like_count", 0),
                review.get("reply_count", 0),
                len(review.get("image_urls", [])),
                len(review.get("video_urls", []))
            ])
        
        wb.save(file_path)
        utils.logger.info(f"[CtripStoreFactory._save_to_excel] Saved {len(_reviews_data)} reviews to {file_path}")


async def save_review(review: CtripReview) -> None:
    """Save review"""
    await CtripStoreFactory.save_review(review)


async def save_data_to_file() -> None:
    """Save data to file"""
    await CtripStoreFactory.save_data_to_file()


async def update_ctrip_review_image(review_id: str, index: int, pic_content: bytes, image_url: str) -> None:
    """
    Save review image
    """
    # Extract file extension from URL
    extension = image_url.split(".")[-1] if "." in image_url else "jpg"
    extension = extension.split("?")[0]  # Remove query params
    
    pic_id = f"{review_id}_{index}"
    await CtripStoreImage().store_image({
        "pic_id": pic_id,
        "pic_content": pic_content,
        "extension_file_name": extension
    })


async def update_ctrip_review_video(review_id: str, index: int, video_content: bytes, video_url: str) -> None:
    """
    Save review video
    """
    # Extract file extension from URL
    extension = video_url.split(".")[-1] if "." in video_url else "mp4"
    extension = extension.split("?")[0]  # Remove query params
    
    video_id = f"{review_id}_{index}"
    await CtripStoreVideo().store_video({
        "video_id": video_id,
        "video_content": video_content,
        "extension_file_name": extension
    })

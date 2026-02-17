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

from typing import Optional, List
from pydantic import BaseModel, Field


class CtripReview(BaseModel):
    """
    Ctrip travel review/note model
    """
    review_id: str = Field(default="", description="Review ID")
    title: str = Field(default="", description="Review title")
    content: str = Field(default="", description="Review content")
    review_url: str = Field(default="", description="Review URL")
    
    # Author info
    user_id: str = Field(default="", description="Author user ID")
    user_nickname: str = Field(default="", description="Author nickname")
    user_avatar: str = Field(default="", description="Author avatar URL")
    
    # Review metadata
    created_time: int = Field(default=0, description="Create timestamp")
    updated_time: int = Field(default=0, description="Update timestamp")
    view_count: int = Field(default=0, description="View count")
    like_count: int = Field(default=0, description="Like count")
    reply_count: int = Field(default=0, description="Reply/Comment count")
    
    # POI/Destination info
    poi_id: str = Field(default="", description="POI/Destination ID")
    poi_name: str = Field(default="", description="POI/Destination name")
    
    # Search context
    source_keyword: str = Field(default="", description="Source search keyword")
    
    # Media URLs
    image_urls: List[str] = Field(default_factory=list, description="Image URLs")
    video_urls: List[str] = Field(default_factory=list, description="Video URLs")


class CtripComment(BaseModel):
    """
    Ctrip comment model
    """
    comment_id: str = Field(default="", description="Comment ID")
    content: str = Field(default="", description="Comment content")
    created_time: int = Field(default=0, description="Create timestamp")
    
    user_id: str = Field(default="", description="User ID")
    user_nickname: str = Field(default="", description="User nickname")
    
    review_id: str = Field(default="", description="Review ID this comment belongs to")
    like_count: int = Field(default=0, description="Like count")
    
    image_urls: List[str] = Field(default_factory=list, description="Image URLs in comment")

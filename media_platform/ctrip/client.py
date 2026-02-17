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

from typing import Optional
import httpx
import json
from tools import utils


class CtripClient:
    """
    Ctrip API client for fetching travel reviews and notes
    """
    
    def __init__(self):
        self.base_url = "https://www.ctrip.com"
        self.api_url = "https://you.ctrip.com/api"
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        self.timeout = 10
        
    async def search_reviews(self, keyword: str, page: int = 1, timeout: Optional[int] = None) -> Optional[dict]:
        """
        Search travel reviews with keyword
        
        Args:
            keyword: Search keyword (destination name, POI, etc.)
            page: Page number
            timeout: Request timeout
            
        Returns:
            API response dict or None on error
        """
        try:
            # Construct search URL for Ctrip's travel notes
            url = f"{self.base_url}/you/search/searchresult.aspx?keywords={keyword}&PageIndex={page}"
            
            async with httpx.AsyncClient(timeout=timeout or self.timeout) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": self.user_agent},
                    follow_redirects=True
                )
                
                if response.status_code == 200:
                    return {"status": 200, "data": response.text}
                else:
                    utils.logger.warning(f"[CtripClient.search_reviews] Request failed with status {response.status_code}")
                    return None
        except Exception as exc:
            utils.logger.error(f"[CtripClient.search_reviews] Exception: {exc}")
            return None
    
    async def get_review_detail(self, review_id: str, timeout: Optional[int] = None) -> Optional[dict]:
        """
        Get review detail
        
        Args:
            review_id: Review ID
            timeout: Request timeout
            
        Returns:
            API response dict or None on error
        """
        try:
            url = f"{self.base_url}/you/travels/{review_id}.html"
            
            async with httpx.AsyncClient(timeout=timeout or self.timeout) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": self.user_agent},
                    follow_redirects=True
                )
                
                if response.status_code == 200:
                    return {"status": 200, "data": response.text}
                else:
                    utils.logger.warning(f"[CtripClient.get_review_detail] Request failed with status {response.status_code}")
                    return None
        except Exception as exc:
            utils.logger.error(f"[CtripClient.get_review_detail] Exception: {exc}")
            return None
    
    async def get_image(self, image_url: str, timeout: Optional[int] = None) -> Optional[bytes]:
        """
        Download image content
        
        Args:
            image_url: Image URL
            timeout: Request timeout
            
        Returns:
            Image bytes or None on error
        """
        try:
            async with httpx.AsyncClient(timeout=timeout or self.timeout) as client:
                response = await client.get(
                    image_url,
                    headers={"User-Agent": self.user_agent},
                    follow_redirects=True
                )
                
                if response.status_code == 200:
                    return response.content
                else:
                    utils.logger.warning(f"[CtripClient.get_image] Request {image_url} failed with status {response.status_code}")
                    return None
        except Exception as exc:
            utils.logger.error(f"[CtripClient.get_image] Exception for {image_url}: {exc}")
            return None
    
    async def get_video(self, video_url: str, timeout: Optional[int] = None) -> Optional[bytes]:
        """
        Download video content
        
        Args:
            video_url: Video URL
            timeout: Request timeout
            
        Returns:
            Video bytes or None on error
        """
        try:
            async with httpx.AsyncClient(timeout=timeout or self.timeout) as client:
                response = await client.get(
                    video_url,
                    headers={"User-Agent": self.user_agent},
                    follow_redirects=True
                )
                
                if response.status_code == 200:
                    return response.content
                else:
                    utils.logger.warning(f"[CtripClient.get_video] Request {video_url} failed with status {response.status_code}")
                    return None
        except Exception as exc:
            utils.logger.error(f"[CtripClient.get_video] Exception for {video_url}: {exc}")
            return None

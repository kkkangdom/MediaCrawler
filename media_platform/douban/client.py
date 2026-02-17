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

import asyncio
from typing import Optional
import httpx
from tools import utils


class DoubanClient:
    """
    Douban API client for fetching posts and comments
    """
    
    def __init__(self):
        self.base_url = "https://www.douban.com"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.timeout = 10
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.douban.com/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "max-age=0",
        }
        
    async def search_posts(self, keyword: str, group_id: str = "", page: int = 1, timeout: Optional[int] = None) -> Optional[dict]:
        """
        Search posts in douban with keyword
        
        Args:
            keyword: Search keyword
            group_id: Optional group/topic ID to search within
            page: Page number
            timeout: Request timeout
            
        Returns:
            API response dict or None on error
        """
        try:
            if group_id:
                url = f"{self.base_url}/group/{group_id}/discussion?search={keyword}&start={(page-1)*20}"
            else:
                # 豆瓣小组讨论搜索 URL
                url = f"{self.base_url}/group/1/discussion?search={keyword}&start={(page-1)*20}"
            
            async with httpx.AsyncClient(timeout=timeout or self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    return {"status": 200, "data": response.text}
                else:
                    utils.logger.warning(f"[DoubanClient.search_posts] Request failed with status {response.status_code}, URL: {url}")
                    return None
        except Exception as exc:
            utils.logger.error(f"[DoubanClient.search_posts] Exception: {exc}")
            return None
    
    async def get_post_detail(self, post_id: str, timeout: Optional[int] = None) -> Optional[dict]:
        """
        Get post detail
        
        Args:
            post_id: Post ID
            timeout: Request timeout
            
        Returns:
            API response dict or None on error
        """
        try:
            url = f"{self.base_url}/group/topic/{post_id}/"
            
            async with httpx.AsyncClient(timeout=timeout or self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    return {"status": 200, "data": response.text}
                else:
                    utils.logger.warning(f"[DoubanClient.get_post_detail] Request failed with status {response.status_code}")
                    return None
        except Exception as exc:
            utils.logger.error(f"[DoubanClient.get_post_detail] Exception: {exc}")
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
            async with httpx.AsyncClient(timeout=timeout or self.timeout, follow_redirects=True) as client:
                response = await client.get(image_url, headers=self.headers)
                
                if response.status_code == 200:
                    return response.content
                else:
                    utils.logger.warning(f"[DoubanClient.get_image] Request failed with status {response.status_code}")
                    return None
        except Exception as exc:
            utils.logger.error(f"[DoubanClient.get_image] Exception: {exc}")
            return None

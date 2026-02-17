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

import re
from typing import List
from parsel import Selector


class CtripExtractor:
    """
    Extract data from Ctrip HTML content
    """
    
    @staticmethod
    def extract_reviews_from_search(html_content: str) -> List[dict]:
        """
        Extract reviews from search results page
        
        Args:
            html_content: HTML content of search results
            
        Returns:
            List of review dictionaries with basic info
        """
        selector = Selector(text=html_content)
        reviews = []
        
        # Extract from search result items
        review_elements = selector.xpath('//div[@class="travelListBox"]//div[@class="travelItem"]')
        
        for element in review_elements:
            try:
                review_link = element.xpath('./a/@href').get("")
                review_title = element.xpath('.//h3/a/text()').get("").strip()
                
                # Extract review ID from URL
                review_id = review_link.split("/")[-1].split(".")[0] if review_link else ""
                
                author = element.xpath('.//div[@class="author"]/a/text()').get("").strip()
                location = element.xpath('.//div[@class="destName"]/a/text()').get("").strip()
                view_count = element.xpath('.//span[@class="viewCount"]/text()').get("0").strip()
                
                if review_id and review_title:
                    reviews.append({
                        "review_id": review_id,
                        "title": review_title,
                        "review_link": review_link,
                        "author": author,
                        "location": location,
                        "view_count": view_count
                    })
            except Exception:
                continue
                
        return reviews
    
    @staticmethod
    def extract_review_detail(html_content: str) -> dict:
        """
        Extract review detail from review page
        
        Args:
            html_content: HTML content of review page
            
        Returns:
            Dict containing review detail info
        """
        selector = Selector(text=html_content)
        
        review_data = {
            "title": "",
            "content": "",
            "author": "",
            "created_time": "",
            "views": 0,
            "likes": 0,
            "comments": 0,
            "images": [],
            "videos": []
        }
        
        # Extract title
        review_data["title"] = selector.xpath('//h1[@class="articleTitle"]/text()').get("").strip()
        
        # Extract content
        content_parts = selector.xpath('//div[@class="articleContent"]//text()').getall()
        review_data["content"] = "".join(content_parts).strip()
        
        # Extract author info
        review_data["author"] = selector.xpath('//div[@class="authorInfo"]//a/text()').get("").strip()
        
        # Extract created time
        created_text = selector.xpath('//div[@class="travelTime"]/text()').get("")
        review_data["created_time"] = created_text.strip()
        
        # Extract image URLs
        image_urls = selector.xpath('//div[@class="articleContent"]//img/@src').getall()
        review_data["images"] = [url for url in image_urls if url]
        
        # Extract video URLs
        video_urls = selector.xpath('//video/@src').getall()
        review_data["videos"] = [url for url in video_urls if url]
        
        # Extract view count
        view_text = selector.xpath('//span[@class="views"]/text()').get("0")
        review_data["views"] = int(view_text) if view_text.isdigit() else 0
        
        # Extract likes
        like_text = selector.xpath('//span[@class="upCount"]/text()').get("0")
        review_data["likes"] = int(like_text) if like_text.isdigit() else 0
        
        return review_data
    
    @staticmethod
    def extract_image_urls(html_content: str) -> List[str]:
        """
        Extract all image URLs from HTML content
        
        Args:
            html_content: HTML content
            
        Returns:
            List of image URLs
        """
        selector = Selector(text=html_content)
        
        image_urls = []
        
        # From img tags
        img_srcs = selector.xpath('//img/@src').getall()
        image_urls.extend(img_srcs)
        
        # From data-src (lazy loaded images)
        img_data_srcs = selector.xpath('//img/@data-src').getall()
        image_urls.extend(img_data_srcs)
        
        # Filter and deduplicate
        image_urls = [url for url in image_urls if url and ("image" in url or "pic" in url or "ctrip" in url)]
        
        return list(dict.fromkeys(image_urls))
    
    @staticmethod
    def extract_video_urls(html_content: str) -> List[str]:
        """
        Extract all video URLs from HTML content
        
        Args:
            html_content: HTML content
            
        Returns:
            List of video URLs
        """
        selector = Selector(text=html_content)
        
        video_urls = []
        
        # From video tags
        video_srcs = selector.xpath('//video/@src').getall()
        video_urls.extend(video_srcs)
        
        # From iframe sources
        iframe_srcs = selector.xpath('//iframe/@src').getall()
        video_urls.extend([url for url in iframe_srcs if url and ("video" in url or "youku" in url or "bilibili" in url)])
        
        return list(dict.fromkeys(video_urls))

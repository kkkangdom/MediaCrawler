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


class DoubanExtractor:
    """
    Extract data from Douban HTML content
    """
    
    @staticmethod
    def extract_posts_from_search(html_content: str) -> List[dict]:
        """
        Extract posts from Douban search results page (全站搜索)
        Supports both diary entries and group discussions
        
        Args:
            html_content: HTML content of search results
            
        Returns:
            List of post dictionaries with basic info
        """
        selector = Selector(text=html_content)
        posts = []
        
        # 方法1：从全站搜索结果页面提取日记（<div class="result">）
        result_items = selector.xpath('//div[@class="result"]')
        for item in result_items:
            try:
                # 获取帖子链接和标题（在 h3 -> a 标签中）
                title_elem = item.xpath('.//h3/a')
                post_link = title_elem.xpath('@href').get("").strip()
                # 提取 <a> 标签中的文本，忽略前面的 [日记] 等标签
                post_title = title_elem.xpath('text()').get("").strip()
                
                # 从链接中提取帖子ID（日记格式：/note/XXXXX/）
                post_id = ""
                if post_link:
                    # 如果是link2重定向，从onclick中提取sid
                    if "link2" in post_link:
                        match = re.search(r"sid:\s*(\d+)", item.xpath('.//h3/a/@onclick').get(""))
                        if match:
                            post_id = match.group(1)
                    # 日记格式
                    match = re.search(r'/note/(\d+)/?', post_link)
                    if match:
                        post_id = match.group(1)
                    # group/topic格式
                    else:
                        match = re.search(r'/topic/(\d+)/?', post_link)
                        if match:
                            post_id = match.group(1)
                
                # 获取其他信息（日记格式：喜欢数 / 作者）
                info_text = item.xpath('.//div[@class="info"]//text()').getall()
                likes = ""
                author = ""
                if info_text:
                    # 第一个通常是点赞数（如"767 人喜欢"）
                    likes = info_text[0].strip() if len(info_text) > 0 else ""
                    # 其他的是作者名
                    author = info_text[-1].strip() if len(info_text) > 1 else ""
                
                # 获取内容摘要
                content_preview = item.xpath('.//p/text()').get("").strip()
                
                if post_id and post_title:
                    posts.append({
                        "post_id": post_id,
                        "title": post_title,
                        "post_link": post_link,
                        "author": author,
                        "likes": likes,
                        "content_preview": content_preview
                    })
            except Exception as e:
                continue
        
        # 方法2：从讨论列表行提取（group内搜索的备选方案）
        if not posts:
            post_elements = selector.xpath('//tr[@class="tr3"]')
            for element in post_elements:
                try:
                    post_link = element.xpath('./td[1]/a/@href').get("")
                    post_title = element.xpath('./td[1]/a/text()').get("").strip()
                    post_id = post_link.split("/")[-2] if post_link else ""
                    author = element.xpath('./td[2]/a/text()').get("").strip()
                    reply_count = element.xpath('./td[3]/text()').get("0").strip()
                    created_time = element.xpath('./td[4]/text()').get("").strip()
                    
                    if post_id and post_title:
                        posts.append({
                            "post_id": post_id,
                            "title": post_title,
                            "post_link": post_link,
                            "author": author,
                            "reply_count": reply_count,
                            "created_time": created_time
                        })
                except Exception:
                    continue
        
        # 方法3：使用更宽松的正则表达式匹配
        if not posts:
            # 提取所有看起来像是豆瓣日记的链接
            diary_links = re.findall(r'href="([^"]*note/(\d+)[^"]*)"[^>]*>([^<]+)<', html_content)
            for link, post_id, title in diary_links:
                if post_id and title:
                    posts.append({
                        "post_id": post_id.strip(),
                        "title": title.strip(),
                        "post_link": link,
                        "author": "",
                        "likes": "0",
                        "content_preview": ""
                    })
                
        return posts
    
    @staticmethod
    def extract_post_detail(html_content: str) -> dict:
        """
        Extract post detail from Douban diary/note page
        
        Args:
            html_content: HTML content of post page
            
        Returns:
            Dict containing post detail info
        """
        selector = Selector(text=html_content)
        
        post_data = {
            "title": "",
            "content": "",
            "author": "",
            "created_time": "",
            "likes": 0,
            "replies": 0,
            "images": []
        }
        
        # 提取标题 - 从 <title> 标签中提取
        title = selector.xpath('//title/text()').get("").strip()
        post_data["title"] = title if title else ""
        
        # 提取内容 - 这是最重要的部分
        content = ""
        
        # 方法1: 正确的日记页面结构 - #note_{{id}}_full > div#link-report > div.note > p
        # 获取所有 <p> 标签中的文本（这些是文章正文段落）
        paragraphs = selector.xpath('//*[@id="link-report"]//div[@class="note"]/p/text()').getall()
        if paragraphs:
            content = "".join(paragraphs).strip()
        
        # 方法2: 如果上面没找到，尝试所有 p 标签
        if not content:
            content_parts = selector.xpath('//div[@class="note"]//p//text()').getall()
            if content_parts:
                content = "".join(content_parts).strip()
        
        # 方法3: 尝试标准的 note-content div
        if not content:
            content_parts = selector.xpath('//div[@class="note-content"]//text()').getall()
            if content_parts:
                content = "".join(content_parts).strip()
        
        # 方法4: 尝试 note-text
        if not content:
            content_parts = selector.xpath('//div[@class="note-text"]//text()').getall()
            if content_parts:
                content = "".join(content_parts).strip()
        
        # 方法5: 尝试通用 content div
        if not content:
            content_parts = selector.xpath('//div[@class="content"]//text()').getall()
            if content_parts:
                content = "".join(content_parts).strip()
        
        # 方法6: 正则提取所有 <p> 标签内容
        if not content:
            matches = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL)
            if matches:
                # 过滤掉评论区的 <p> 标签，只取前面的内容
                # 评论区通常在 <div class="note"> 后面很远的地方
                filtered_matches = []
                for match in matches:
                    # 过滤掉包含评论相关HTML的匹配
                    if 'comment' not in match.lower() and 'form-area' not in match.lower():
                        # 移除HTML标签
                        text = re.sub(r'<[^>]+>', '', match).strip()
                        if text and len(text) > 5:  # 只要长度足够的内容
                            filtered_matches.append(text)
                
                if filtered_matches:
                    # 取前20个段落（避免取到评论）
                    content = "".join(filtered_matches[:20]).strip()
        
        post_data["content"] = content
        
        # 提取作者
        author = selector.xpath('//a[@class="note-author"]/text()').get("")
        if not author:
            author = selector.xpath('//span[@class="note-author"]/a/text()').get("")
        if not author:
            # 从数据属性提取
            author = selector.xpath('//*[@id="note-801470947"]/@data-author').get("")
        post_data["author"] = author.strip() if author else ""
        
        # 提取创建时间 - 从 span.pub-date 中
        created_time = selector.xpath('//span[@class="pub-date"]/text()').get("")
        if not created_time:
            created_time = selector.xpath('//span[@class="color-desc"]/text()').get("")
        post_data["created_time"] = created_time.strip() if created_time else ""
        
        # 提取点赞数
        like_text = selector.xpath('//div[@class="likes-num"]/text()').get("")
        if like_text:
            like_match = re.search(r'(\d+)', like_text)
            post_data["likes"] = int(like_match.group(1)) if like_match else 0
        
        # 提取图片
        image_urls = selector.xpath('//div[@id="link-report"]//img/@src').getall()
        if not image_urls:
            image_urls = selector.xpath('//div[@class="note"]//img/@src').getall()
        if not image_urls:
            image_urls = selector.xpath('//img/@src').getall()
        post_data["images"] = [url for url in image_urls if url and ('pic' in url or 'view' in url or 'douban' in url)]
        
        return post_data
    
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
        
        # Extract images from various contexts
        image_urls = []
        
        # From img tags in content
        img_srcs = selector.xpath('//img/@src').getall()
        image_urls.extend(img_srcs)
        
        # From data-src (lazy loaded images)
        img_data_srcs = selector.xpath('//img/@data-src').getall()
        image_urls.extend(img_data_srcs)
        
        # Filter and deduplicate
        image_urls = [url for url in image_urls if url and ("pic" in url or "image" in url or "douban" in url)]
        
        return list(dict.fromkeys(image_urls))  # Remove duplicates while preserving order

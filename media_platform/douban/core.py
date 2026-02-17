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
import os
from typing import Dict, List, Optional
import time
from urllib.parse import quote

from playwright.async_api import (
    BrowserContext,
    BrowserType,
    Page,
    Playwright,
    async_playwright,
)

import config
from base.base_crawler import AbstractCrawler
from model.m_douban import DoubanPost, DoubanComment
from proxy.proxy_ip_pool import IpInfoModel, create_ip_pool
from store import douban as douban_store
from tools import utils
from tools.cdp_browser import CDPBrowserManager
from var import crawler_type_var, source_keyword_var

from .client import DoubanClient
from .help import DoubanExtractor
from .login import DoubanLogin


class DoubanCrawler(AbstractCrawler):
    context_page: Page
    douban_client: DoubanClient
    browser_context: BrowserContext
    cdp_manager: Optional[CDPBrowserManager]

    def __init__(self) -> None:
        self.index_url = "https://www.douban.com"
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        self._extractor = DoubanExtractor()
        self.cdp_manager = None
        self.ip_proxy_pool = None

    async def _download_media_for_post(self, post: DoubanPost) -> None:
        """Download images for a post"""
        if not config.ENABLE_GET_MEIDAS:
            return
        if not post or not post.image_urls:
            return

        for index, url in enumerate(post.image_urls or [], start=1):
            media = await self.douban_client.get_image(url)
            if media:
                await douban_store.update_douban_post_image(post.post_id, index, media, url)
            await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)

    async def start(self) -> None:
        """Start the crawler"""
        utils.logger.info("[DoubanCrawler.start] Begin crawler")
        try:
            await self.search()
        finally:
            await douban_store.save_data_to_file()

    async def search(self) -> None:
        """Search posts by keyword using browser automation with anti-crawl mechanisms"""
        utils.logger.info(f"[DoubanCrawler.search] Begin search keyword: {config.KEYWORDS}")
        
        # Initialize proxy if enabled
        playwright_proxy_format, httpx_proxy_format = None, None
        if config.ENABLE_IP_PROXY:
            utils.logger.info("[DoubanCrawler.search] Initializing proxy IP pool...")
            self.ip_proxy_pool = await create_ip_pool(config.IP_PROXY_POOL_COUNT, enable_validate_ip=True)
            ip_proxy_info: IpInfoModel = await self.ip_proxy_pool.get_proxy()
            playwright_proxy_format, httpx_proxy_format = utils.format_proxy_info(ip_proxy_info)
            utils.logger.info(f"[DoubanCrawler.search] Using proxy: {ip_proxy_info.ip}:{ip_proxy_info.port}")

        # Initialize HTTP client for image downloads
        self.douban_client = DoubanClient()
        
        try:
            # Use browser automation with anti-detection features
            async with async_playwright() as playwright:
                # Choose launch mode based on configuration
                if config.ENABLE_CDP_MODE:
                    utils.logger.info("[DoubanCrawler] Launching browser using CDP mode")
                    self.browser_context = await self.launch_browser_with_cdp(
                        playwright,
                        playwright_proxy_format,
                        self.user_agent,
                        headless=config.CDP_HEADLESS,
                    )
                else:
                    utils.logger.info("[DoubanCrawler] Launching browser using standard mode")
                    chromium = playwright.chromium
                    self.browser_context = await self.launch_browser(
                        chromium,
                        playwright_proxy_format,
                        self.user_agent,
                        headless=config.HEADLESS,
                    )
                    # Inject stealth scripts to bypass anti-bot detection
                    await self.browser_context.add_init_script(path="libs/stealth.min.js")

                self.context_page = await self.browser_context.new_page()
                
                # Navigate to index page first to establish session
                await self.context_page.goto(self.index_url, wait_until="domcontentloaded")
                await asyncio.sleep(2)
                
                # Check if login is needed and perform login if configured
                await self._check_and_login()
                
                # Search with pagination
                for page_num in range(1, config.CRAWLER_MAX_PAGES + 1):
                    try:
                        utils.logger.info(f"[DoubanCrawler.search] Searching page {page_num}")
                        
                        # Build search URL - using full site search with diary category (cat=1015)
                        # URL encode the keyword for proper handling of Chinese characters
                        encoded_keyword = quote(config.KEYWORDS)
                        url = f"https://www.douban.com/search?source=suggest&q={encoded_keyword}&cat=1015&start={(page_num-1)*20}"
                        utils.logger.info(f"[DoubanCrawler.search] Navigating to: {url}")
                        
                        # Navigate with multiple wait strategies
                        try:
                            await self.context_page.goto(url, wait_until="networkidle", timeout=60000)
                        except:
                            # If networkidle times out, fall back to domcontentloaded
                            try:
                                await self.context_page.goto(url, wait_until="domcontentloaded", timeout=30000)
                            except Exception as e:
                                utils.logger.warning(f"[DoubanCrawler.search] Navigation failed: {e}, retrying...")
                                await asyncio.sleep(5)
                                continue
                        
                        # Wait for potential dynamic content to load
                        await self.context_page.wait_for_timeout(3000)
                        await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                        
                        # Get page content
                        page_content = await self.context_page.content()
                        
                        # Debug: save page content to file for analysis
                        debug_file = f"/tmp/douban_page_{page_num}.html"
                        with open(debug_file, "w", encoding="utf-8") as f:
                            f.write(page_content)
                        utils.logger.info(f"[DoubanCrawler.search] Page saved to {debug_file} for debugging")
                        
                        # Check if page is blocked/requires login
                        if self._is_page_blocked(page_content):
                            utils.logger.error("[DoubanCrawler.search] Page is blocked or requires login")
                            utils.logger.info("[DoubanCrawler.search] Try the following solutions:")
                            utils.logger.info("1. Enable IP proxy: Set ENABLE_IP_PROXY=True in config")
                            utils.logger.info("2. Use cookie login: Set LOGIN_TYPE='cookie' and provide COOKIES")
                            utils.logger.info("3. Use other platforms: xhs, dy, zhihu, etc.")
                            break
                        
                        # Extract posts from page
                        posts = self._extractor.extract_posts_from_search(page_content)
                        
                        if not posts:
                            utils.logger.info(f"[DoubanCrawler.search] No posts found on page {page_num}, stopping")
                            break
                        
                        utils.logger.info(f"[DoubanCrawler.search] Found {len(posts)} posts on page {page_num}")
                        
                        # Process each post
                        for post_info in posts:
                            try:
                                post_id = post_info.get("post_id")
                                if not post_id:
                                    continue
                                
                                # Build detail URL based on post_link if available, otherwise construct it
                                detail_url = post_info.get("post_link", "")
                                if not detail_url:
                                    # Fallback: construct URL assuming group/topic format
                                    detail_url = f"https://www.douban.com/group/topic/{post_id}/"
                                
                                # Handle link2 redirect URLs from search results
                                if "link2" in detail_url:
                                    # Extract the real URL from link2 redirect
                                    try:
                                        # Navigate to the link2 URL which will redirect
                                        await self.context_page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
                                        await asyncio.sleep(1)
                                        # Get the final URL after redirect
                                        detail_url = self.context_page.url
                                    except:
                                        continue
                                
                                utils.logger.info(f"[DoubanCrawler.search] Fetching post detail: {detail_url}")
                                
                                await self.context_page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
                                await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                                
                                detail_content = await self.context_page.content()
                                
                                # Debug: save first post detail page for analysis
                                if post_id == "801470947":  # Save first post as sample
                                    with open("/tmp/douban_detail_sample.html", "w", encoding="utf-8") as f:
                                        f.write(detail_content)
                                    utils.logger.info("[DoubanCrawler.search] Saved sample detail page to /tmp/douban_detail_sample.html")
                                
                                post_detail = self._extractor.extract_post_detail(detail_content)
                                all_images = self._extractor.extract_image_urls(detail_content)
                                
                                # Log extracted content for debugging
                                utils.logger.info(f"[DoubanCrawler.search] Extracted post detail - Title: {post_detail.get('title', '')[:50]}, Content length: {len(post_detail.get('content', ''))}")
                                if post_detail.get('content'):
                                    utils.logger.info(f"[DoubanCrawler.search] Content preview: {post_detail.get('content', '')[:100]}...")
                                
                                # Create DoubanPost object
                                post = DoubanPost(
                                    post_id=post_id,
                                    title=post_detail.get("title", "") or post_info.get("title", ""),
                                    content=post_detail.get("content", ""),
                                    content_url=detail_url,
                                    user_nickname=post_detail.get("author", "") or post_info.get("author", ""),
                                    created_time=int(time.time()),
                                    like_count=post_detail.get("likes", 0),
                                    reply_count=int(post_detail.get("replies", 0)),
                                    source_keyword=config.KEYWORDS,
                                    image_urls=all_images
                                )
                                
                                # Save post
                                await douban_store.save_post(post)
                                utils.logger.info(f"[DoubanCrawler.search] Successfully saved post: {post_id}")
                                
                                # Download images if enabled
                                if config.ENABLE_GET_MEIDAS and all_images:
                                    for index, img_url in enumerate(all_images, start=1):
                                        try:
                                            utils.logger.info(f"[DoubanCrawler.search] Downloading image {index}/{len(all_images)}")
                                            img_data = await self.douban_client.get_image(img_url)
                                            if img_data:
                                                await douban_store.update_douban_post_image(post_id, index, img_data, img_url)
                                        except Exception as e:
                                            utils.logger.warning(f"[DoubanCrawler.search] Failed to download image {index}: {e}")
                                        await asyncio.sleep(1)
                                
                                await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                                
                            except Exception as e:
                                utils.logger.error(f"[DoubanCrawler.search] Error processing post {post_info.get('post_id')}: {e}")
                                continue
                        
                        # Sleep between pages
                        await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC * 2)
                        
                    except Exception as e:
                        utils.logger.error(f"[DoubanCrawler.search] Error on page {page_num}: {e}")
                        continue
                
                await self.browser_context.close()
        
        except Exception as e:
            utils.logger.error(f"[DoubanCrawler.search] Fatal error: {e}")
            raise
    
    def _is_page_blocked(self, page_content: str) -> bool:
        """Check if page is blocked or requires login"""
        blocked_indicators = [
            "有异常请求从你的 IP 发出",
            "登录跳转页",
            "请登录使用豆瓣",
            "access denied",
            "403",
            "robot",
        ]
        
        content_lower = page_content.lower()
        for indicator in blocked_indicators:
            if indicator.lower() in content_lower:
                utils.logger.warning(f"[DoubanCrawler._is_page_blocked] Found blocking indicator: {indicator}")
                return True
        
        # Also check if we have search results, which means page is NOT blocked
        if "result-list" in page_content or '<div class="result">' in page_content:
            utils.logger.info("[DoubanCrawler._is_page_blocked] Found search results, page is accessible")
            return False
        
        return False
    
    async def _check_and_login(self) -> None:
        """Check if login is needed and perform login if configured"""
        # Check current page for login requirement
        try:
            page_content = await self.context_page.content()
            
            # If page is not blocked, no login needed
            if not self._is_page_blocked(page_content):
                utils.logger.info("[DoubanCrawler._check_and_login] No login required")
                return
            
            # Perform login based on configured login type
            if config.LOGIN_TYPE == "qrcode":
                utils.logger.info("[DoubanCrawler._check_and_login] Starting QR code login...")
                login_obj = DoubanLogin(
                    login_type="qrcode",
                    browser_context=self.browser_context,
                    context_page=self.context_page,
                )
                await login_obj.begin()
                
            elif config.LOGIN_TYPE == "phone":
                utils.logger.info("[DoubanCrawler._check_and_login] Starting SMS login...")
                if not config.LOGIN_PHONE:
                    utils.logger.error("[DoubanCrawler._check_and_login] LOGIN_PHONE not configured")
                    return
                
                login_obj = DoubanLogin(
                    login_type="phone",
                    browser_context=self.browser_context,
                    context_page=self.context_page,
                    login_phone=config.LOGIN_PHONE,
                )
                await login_obj.begin()
                
            elif config.LOGIN_TYPE == "cookie":
                utils.logger.info("[DoubanCrawler._check_and_login] Using cookie login...")
                if not config.COOKIES:
                    utils.logger.warning("[DoubanCrawler._check_and_login] COOKIES not configured, skipping cookie login")
                    return
                
                login_obj = DoubanLogin(
                    login_type="cookie",
                    browser_context=self.browser_context,
                    context_page=self.context_page,
                    cookie_str=config.COOKIES,
                )
                await login_obj.begin()
            else:
                utils.logger.warning(f"[DoubanCrawler._check_and_login] Unknown LOGIN_TYPE: {config.LOGIN_TYPE}")
        
        except Exception as e:
            utils.logger.error(f"[DoubanCrawler._check_and_login] Login failed: {e}")

    async def launch_browser(
        self,
        chromium: BrowserType,
        playwright_proxy: Optional[Dict],
        user_agent: Optional[str],
        headless: bool = True,
    ) -> BrowserContext:
        """Launch browser and create browser context"""
        utils.logger.info("[DoubanCrawler.launch_browser] Begin create browser context ...")
        
        # Prepare launch arguments with anti-detection features
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-web-resources-dep-cache",
            "--disable-client-side-phishing-detection",
        ]
        
        if config.SAVE_LOGIN_STATE:
            # Save login state to avoid repeated login
            user_data_dir = os.path.join(os.getcwd(), "browser_data", config.USER_DATA_DIR % config.PLATFORM)
            os.makedirs(user_data_dir, exist_ok=True)
            browser_context = await chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                accept_downloads=True,
                headless=headless,
                proxy=playwright_proxy,
                viewport={"width": 1920, "height": 1080},
                user_agent=user_agent,
                args=launch_args,
            )
            return browser_context
        else:
            # Launch browser without persistent context
            browser = await chromium.launch(
                headless=headless,
                proxy=playwright_proxy,
                args=launch_args,
            )
            browser_context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=user_agent,
            )
            return browser_context

    async def launch_browser_with_cdp(
        self,
        playwright: Playwright,
        playwright_proxy: Optional[Dict],
        user_agent: Optional[str],
        headless: bool = True,
    ) -> BrowserContext:
        """Launch browser using CDP mode"""
        try:
            self.cdp_manager = CDPBrowserManager()
            browser_context = await self.cdp_manager.launch_and_connect(
                playwright=playwright,
                playwright_proxy=playwright_proxy,
                user_agent=user_agent,
                headless=headless,
            )

            # Display browser information
            browser_info = await self.cdp_manager.get_browser_info()
            utils.logger.info(f"[DoubanCrawler] CDP browser info: {browser_info}")

            return browser_context

        except Exception as e:
            utils.logger.error(f"[DoubanCrawler] CDP mode launch failed, falling back to standard mode: {e}")
            # Fall back to standard mode
            chromium = playwright.chromium
            return await self.launch_browser(
                chromium, playwright_proxy, user_agent, headless
            )

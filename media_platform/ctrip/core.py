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
from typing import Dict, Optional
import time

from playwright.async_api import (
    BrowserContext,
    BrowserType,
    Page,
    Playwright,
    async_playwright,
)

import config
from base.base_crawler import AbstractCrawler
from model.m_ctrip import CtripReview, CtripComment
from proxy.proxy_ip_pool import IpInfoModel, create_ip_pool
from store import ctrip as ctrip_store
from tools import utils
from tools.cdp_browser import CDPBrowserManager
from var import crawler_type_var, source_keyword_var

from .client import CtripClient
from .help import CtripExtractor
from .login import CtripLogin


class CtripCrawler(AbstractCrawler):
    context_page: Optional[Page]
    ctrip_client: CtripClient
    browser_context: Optional[BrowserContext]
    cdp_manager: Optional[CDPBrowserManager]

    def __init__(self) -> None:
        self.index_url = "https://www.ctrip.com"
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        self._extractor = CtripExtractor()
        self.cdp_manager = None
        self.ip_proxy_pool = None

    async def _download_media_for_review(self, review: CtripReview) -> None:
        """Download images and videos for a review"""
        if not config.ENABLE_GET_MEIDAS:
            return
        if not review:
            return

        # Download images
        for index, url in enumerate(review.image_urls or [], start=1):
            try:
                media = await self.ctrip_client.get_image(url)
                if media:
                    await ctrip_store.update_ctrip_review_image(review.review_id, index, media, url)
            except Exception as e:
                utils.logger.warning(f"[CtripCrawler._download_media_for_review] Failed to download image {index}: {e}")
            await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)

        # Download videos
        for index, url in enumerate(review.video_urls or [], start=1):
            try:
                media = await self.ctrip_client.get_video(url)
                if media:
                    await ctrip_store.update_ctrip_review_video(review.review_id, index, media, url)
            except Exception as e:
                utils.logger.warning(f"[CtripCrawler._download_media_for_review] Failed to download video {index}: {e}")
            await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)

    async def start(self) -> None:
        """Start the crawler"""
        utils.logger.info("[CtripCrawler.start] Begin crawler")
        try:
            await self.search()
        finally:
            await ctrip_store.save_data_to_file()

    async def search(self) -> None:
        """Search reviews by keyword using browser automation with anti-crawl mechanisms"""
        utils.logger.info(f"[CtripCrawler.search] Begin search keyword: {config.KEYWORDS}")
        
        # Initialize proxy if enabled
        playwright_proxy_format, httpx_proxy_format = None, None
        if config.ENABLE_IP_PROXY:
            utils.logger.info("[CtripCrawler.search] Initializing proxy IP pool...")
            self.ip_proxy_pool = await create_ip_pool(config.IP_PROXY_POOL_COUNT, enable_validate_ip=True)
            ip_proxy_info: IpInfoModel = await self.ip_proxy_pool.get_proxy()
            playwright_proxy_format, httpx_proxy_format = utils.format_proxy_info(ip_proxy_info)
            utils.logger.info(f"[CtripCrawler.search] Using proxy: {ip_proxy_info.ip}:{ip_proxy_info.port}")

        # Initialize HTTP client for image/video downloads
        self.ctrip_client = CtripClient()
        
        try:
            # Use browser automation with anti-detection features
            async with async_playwright() as playwright:
                # Choose launch mode based on configuration
                if config.ENABLE_CDP_MODE:
                    utils.logger.info("[CtripCrawler] Launching browser using CDP mode")
                    self.browser_context = await self.launch_browser_with_cdp(
                        playwright,
                        playwright_proxy_format,
                        self.user_agent,
                        headless=config.CDP_HEADLESS,
                    )
                else:
                    utils.logger.info("[CtripCrawler] Launching browser using standard mode")
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
                for page in range(1, config.CRAWLER_MAX_PAGES + 1):
                    try:
                        utils.logger.info(f"[CtripCrawler.search] Searching page {page}")
                        
                        # Build search URL for Ctrip reviews
                        search_url = f"https://www.ctrip.com/app/travel/travels?search={config.KEYWORDS}&page={page}"
                        utils.logger.info(f"[CtripCrawler.search] Navigating to: {search_url}")
                        
                        # Navigate with multiple wait strategies
                        try:
                            await self.context_page.goto(search_url, wait_until="networkidle", timeout=60000)
                        except:
                            # If networkidle times out, fall back to domcontentloaded
                            try:
                                await self.context_page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
                            except Exception as e:
                                utils.logger.warning(f"[CtripCrawler.search] Navigation failed: {e}, retrying...")
                                await asyncio.sleep(5)
                                continue
                        
                        # Wait for potential dynamic content to load
                        await self.context_page.wait_for_timeout(2000)
                        await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                        
                        # Get page content
                        page_content = await self.context_page.content()
                        
                        # Debug: save page content to file for analysis
                        debug_file = f"/tmp/ctrip_page_{page}.html"
                        with open(debug_file, "w", encoding="utf-8") as f:
                            f.write(page_content)
                        utils.logger.info(f"[CtripCrawler.search] Page saved to {debug_file} for debugging")
                        
                        # Check if page is blocked/requires verification
                        if self._is_page_blocked(page_content):
                            utils.logger.error("[CtripCrawler.search] Page is blocked or requires verification")
                            utils.logger.info("[CtripCrawler.search] Try the following solutions:")
                            utils.logger.info("1. Enable IP proxy: Set ENABLE_IP_PROXY=True in config")
                            utils.logger.info("2. Use cookie login: Set LOGIN_TYPE='cookie' and provide COOKIES")
                            utils.logger.info("3. Use other platforms: xhs, dy, zhihu, etc.")
                            break
                        
                        # Extract reviews from page
                        reviews = self._extractor.extract_reviews_from_search(page_content)
                        
                        if not reviews:
                            utils.logger.info(f"[CtripCrawler.search] No reviews found on page {page}, stopping")
                            break
                        
                        utils.logger.info(f"[CtripCrawler.search] Found {len(reviews)} reviews on page {page}")
                        
                        # Process each review
                        for review_info in reviews:
                            try:
                                review_id = review_info.get("review_id")
                                if not review_id:
                                    continue
                                
                                # Navigate to review detail page
                                detail_url = f"https://www.ctrip.com/you/travels/{review_id}.html"
                                utils.logger.info(f"[CtripCrawler.search] Fetching review detail: {detail_url}")
                                
                                await self.context_page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
                                await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                                
                                detail_content = await self.context_page.content()
                                review_detail = self._extractor.extract_review_detail(detail_content)
                                image_urls = self._extractor.extract_image_urls(detail_content)
                                video_urls = self._extractor.extract_video_urls(detail_content)
                                
                                # Create CtripReview object
                                review = CtripReview(
                                    review_id=review_id,
                                    title=review_detail.get("title", ""),
                                    content=review_detail.get("content", ""),
                                    review_url=detail_url,
                                    user_nickname=review_detail.get("author", ""),
                                    poi_name=review_info.get("location", ""),
                                    created_time=int(time.time()),
                                    view_count=review_detail.get("views", 0),
                                    like_count=review_detail.get("likes", 0),
                                    reply_count=review_detail.get("comments", 0),
                                    source_keyword=config.KEYWORDS,
                                    image_urls=image_urls,
                                    video_urls=video_urls
                                )
                                
                                # Save review
                                await ctrip_store.save_review(review)
                                utils.logger.info(f"[CtripCrawler.search] Successfully saved review: {review_id}")
                                
                                # Download media if enabled
                                await self._download_media_for_review(review)
                                
                                # Sleep to avoid rate limiting
                                await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
                                
                            except Exception as e:
                                utils.logger.error(f"[CtripCrawler.search] Error processing review {review_info.get('review_id')}: {e}")
                                continue
                        
                        # Sleep between pages
                        await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC * 2)
                        
                    except Exception as e:
                        utils.logger.error(f"[CtripCrawler.search] Error on page {page}: {e}")
                        continue
                
                await self.browser_context.close()
        
        except Exception as e:
            utils.logger.error(f"[CtripCrawler.search] Fatal error: {e}")
            raise
    
    def _is_page_blocked(self, page_content: str) -> bool:
        """Check if page is blocked or requires verification"""
        blocked_indicators = [
            "anti-robot",
            "验证",
            "verification",
            "robot",
            "403",
            "access denied",
            "请求异常",
        ]
        
        content_lower = page_content.lower()
        for indicator in blocked_indicators:
            if indicator.lower() in content_lower:
                return True
        
        return False
    
    async def _check_and_login(self) -> None:
        """Check if login is needed and perform login if configured"""
        # Check current page for login requirement
        try:
            page_content = await self.context_page.content()
            
            # If page is not blocked, no login needed
            if not self._is_page_blocked(page_content):
                utils.logger.info("[CtripCrawler._check_and_login] No login required")
                return
            
            # Perform login based on configured login type
            if config.LOGIN_TYPE == "qrcode":
                utils.logger.info("[CtripCrawler._check_and_login] Starting QR code login...")
                login_obj = CtripLogin(
                    login_type="qrcode",
                    browser_context=self.browser_context,
                    context_page=self.context_page,
                )
                await login_obj.begin()
                
            elif config.LOGIN_TYPE == "phone":
                utils.logger.info("[CtripCrawler._check_and_login] Starting SMS login...")
                if not config.LOGIN_PHONE:
                    utils.logger.error("[CtripCrawler._check_and_login] LOGIN_PHONE not configured")
                    return
                
                login_obj = CtripLogin(
                    login_type="phone",
                    browser_context=self.browser_context,
                    context_page=self.context_page,
                    login_phone=config.LOGIN_PHONE,
                )
                await login_obj.begin()
                
            elif config.LOGIN_TYPE == "cookie":
                utils.logger.info("[CtripCrawler._check_and_login] Using cookie login...")
                if not config.COOKIES:
                    utils.logger.warning("[CtripCrawler._check_and_login] COOKIES not configured, skipping cookie login")
                    return
                
                login_obj = CtripLogin(
                    login_type="cookie",
                    browser_context=self.browser_context,
                    context_page=self.context_page,
                    cookie_str=config.COOKIES,
                )
                await login_obj.begin()
            else:
                utils.logger.warning(f"[CtripCrawler._check_and_login] Unknown LOGIN_TYPE: {config.LOGIN_TYPE}")
        
        except Exception as e:
            utils.logger.error(f"[CtripCrawler._check_and_login] Login failed: {e}")

    async def launch_browser(
        self,
        chromium: BrowserType,
        playwright_proxy: Optional[Dict],
        user_agent: Optional[str],
        headless: bool = True,
    ) -> BrowserContext:
        """Launch browser and create browser context"""
        utils.logger.info("[CtripCrawler.launch_browser] Begin create browser context ...")
        
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
            utils.logger.info(f"[CtripCrawler] CDP browser info: {browser_info}")

            return browser_context

        except Exception as e:
            utils.logger.error(f"[CtripCrawler] CDP mode launch failed, falling back to standard mode: {e}")
            # Fall back to standard mode
            chromium = playwright.chromium
            return await self.launch_browser(
                chromium, playwright_proxy, user_agent, headless
            )

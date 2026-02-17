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
import functools
import sys
from typing import Optional

from playwright.async_api import BrowserContext, Page
from tenacity import (RetryError, retry, retry_if_result, stop_after_attempt,
                      wait_fixed)

import config
from base.base_crawler import AbstractLogin
from tools import utils


class DoubanLogin(AbstractLogin):
    async def login_by_mobile(self):
        """豆瓣暂不支持 mobile 方式登录，仅为兼容基类接口"""
        raise NotImplementedError("DoubanLogin 不支持 login_by_mobile 方法")
    """豆瓣登录模块，支持二维码、短信验证码和 Cookie 登录"""

    def __init__(
        self,
        login_type: str,
        browser_context: BrowserContext,
        context_page: Page,
        login_phone: Optional[str] = "",
        cookie_str: str = ""
    ):
        config.LOGIN_TYPE = login_type
        self.browser_context = browser_context
        self.context_page = context_page
        self.login_phone = login_phone
        self.cookie_str = cookie_str

    @retry(stop=stop_after_attempt(600), wait=wait_fixed(1), retry=retry_if_result(lambda value: value is False))
    async def check_login_state(self, no_logged_in_session: str) -> bool:
        """检查登录状态"""
        try:
            # 方法 1：检查页面中的个人资料链接
            user_profile_selector = "xpath=//a[contains(@href, '/people/') and contains(@href, '/')]"
            is_visible = await self.context_page.is_visible(user_profile_selector, timeout=500)
            if is_visible:
                utils.logger.info("[DoubanLogin.check_login_state] 检测到个人资料链接，登录成功")
                return True
        except Exception:
            pass

        try:
            # 方法 2：检查登出链接
            logout_selector = "xpath=//a[contains(text(), '退出')]"
            is_visible = await self.context_page.is_visible(logout_selector, timeout=500)
            if is_visible:
                utils.logger.info("[DoubanLogin.check_login_state] 检测到退出链接，登录成功")
                return True
        except Exception:
            pass

        # 方法 3：检查 Cookie 变化
        try:
            current_cookie = await self.browser_context.cookies()
            current_cookies_dict = {c["name"]: c["value"] for c in current_cookie}
            current_dbcl2 = current_cookies_dict.get("dbcl2")
            
            # 豆瓣登录后会设置 dbcl2 Cookie
            if current_dbcl2 and current_dbcl2 != no_logged_in_session:
                utils.logger.info("[DoubanLogin.check_login_state] 检测到 Cookie 变化，登录成功")
                return True
        except Exception as e:
            utils.logger.warning(f"[DoubanLogin.check_login_state] Cookie 检查失败: {e}")

        return False

    async def begin(self):
        """开始登录"""
        utils.logger.info("[DoubanLogin.begin] 开始豆瓣登录...")
        if config.LOGIN_TYPE == "qrcode":
            await self.login_by_qrcode()
        elif config.LOGIN_TYPE == "phone":
            await self.login_by_sms()
        elif config.LOGIN_TYPE == "cookie":
            await self.login_by_cookies()
        else:
            raise ValueError(
                f"[DoubanLogin.begin] 不支持的登录方式: {config.LOGIN_TYPE}. "
                "支持的方式: qrcode, phone, cookie"
            )

    async def login_by_qrcode(self):
        """使用二维码登录豆瓣（增强弹窗自动切换能力）"""
        utils.logger.info("[DoubanLogin.login_by_qrcode] 开始二维码登录...（增强版）")
        try:
            await self.context_page.goto(
                "https://www.douban.com/accounts/login",
                wait_until="domcontentloaded",
                timeout=30000
            )
            await asyncio.sleep(2)

            # 等待弹窗出现
            for _ in range(10):
                try:
                    login_popup = await self.context_page.query_selector("div.account-tabcon")
                    if login_popup:
                        break
                except Exception:
                    pass
                await asyncio.sleep(0.5)

            # 扫码按钮选择器增强
            qrcode_tab_selectors = [
                "xpath=//div[contains(text(), '扫码登录')]",
                "xpath=//button[contains(text(), '扫码登录')]",
                "xpath=//a[contains(text(), '扫码登录')]",
                "xpath=//*[contains(@class, 'qrcode-tab')]",
                "xpath=//span[contains(text(), '扫码登录')]",
                "xpath=//li[contains(text(), '扫码登录')]",
                "xpath=//div[contains(@class, 'tab') and contains(text(), '扫码')]",
                "xpath=//div[contains(@class, 'tab') and contains(., '扫码') and not(contains(@style, 'display: none'))]",
            ]

            # 二维码图片选择器增强
            qrcode_selectors = [
                "xpath=//img[contains(@class, 'qrcode')]",
                "xpath=//img[contains(@src, 'qrcode') or contains(@src, 'qr')]",
                "xpath=//div[contains(@class, 'qr')]//img",
                "img.qrcode-img",
                "xpath=//img[@id='qrcode']",
                "img[src*='qrcode']",
                "img[src*='qr']",
            ]

            # 先尝试直接找二维码
            qrcode_img = None
            for selector in qrcode_selectors:
                try:
                    qrcode_img = await self.context_page.query_selector(selector)
                    if qrcode_img:
                        utils.logger.info(f"[DoubanLogin.login_by_qrcode] 找到二维码: {selector}")
                        break
                except Exception:
                    continue

            # 若未找到二维码，尝试点击扫码按钮
            if not qrcode_img:
                utils.logger.info("[DoubanLogin.login_by_qrcode] 未直接找到二维码，尝试点击扫码登录按钮...")
                for selector in qrcode_tab_selectors:
                    try:
                        element = await self.context_page.wait_for_selector(selector, timeout=3000)
                        if element:
                            await element.click()
                            utils.logger.info(f"[DoubanLogin.login_by_qrcode] 点击扫码登录按钮: {selector}")
                            await asyncio.sleep(2)
                            # 点击后立即查找二维码
                            for _ in range(5):
                                for qrcode_selector in qrcode_selectors:
                                    try:
                                        qrcode_img = await self.context_page.query_selector(qrcode_selector)
                                        if qrcode_img:
                                            utils.logger.info(f"[DoubanLogin.login_by_qrcode] 切换后找到二维码: {qrcode_selector}")
                                            break
                                    except Exception:
                                        continue
                                if qrcode_img:
                                    break
                                await asyncio.sleep(1)
                            if qrcode_img:
                                break
                    except Exception:
                        continue

            if not qrcode_img:
                utils.logger.error("[DoubanLogin.login_by_qrcode] 依然无法找到二维码，登录失败")
                return False

            # 提取二维码图片
            try:
                base64_qrcode_img = await utils.find_login_qrcode(
                    self.context_page,
                    selector="img[class*='qrcode'],img[src*='qrcode'],img[src*='qr']"
                )
            except Exception:
                base64_qrcode_img = None

            if not base64_qrcode_img:
                utils.logger.error("[DoubanLogin.login_by_qrcode] 无法提取二维码图片")
                return False

            # 获取登录前的 dbcl2 Cookie
            current_cookie = await self.browser_context.cookies()
            cookies_dict = {c["name"]: c["value"] for c in current_cookie}
            no_logged_in_dbcl2 = cookies_dict.get("dbcl2", "")

            # 显示二维码给用户扫描
            utils.logger.info("[DoubanLogin.login_by_qrcode] 显示二维码，请用手机扫描...")
            partial_show_qrcode = functools.partial(utils.show_qrcode, base64_qrcode_img)
            asyncio.get_running_loop().run_in_executor(executor=None, func=partial_show_qrcode)

            # 等待用户扫描二维码（最多 120 秒）
            utils.logger.info("[DoubanLogin.login_by_qrcode] 等待用户扫描二维码，剩余时间 120s")
            try:
                await self.check_login_state(no_logged_in_dbcl2)
            except RetryError:
                utils.logger.error("[DoubanLogin.login_by_qrcode] 二维码登录失败或超时")
                return False

            # 登录成功，等待页面重定向
            wait_redirect_seconds = 5
            utils.logger.info(
                f"[DoubanLogin.login_by_qrcode] 登录成功，等待 {wait_redirect_seconds} 秒页面重定向..."
            )
            await asyncio.sleep(wait_redirect_seconds)

            return True
        except Exception as e:
            utils.logger.error(f"[DoubanLogin.login_by_qrcode] 二维码登录异常: {e}")
            return False

    async def login_by_sms(self):
        """使用短信验证码登录豆瓣"""
        utils.logger.info("[DoubanLogin.login_by_sms] 开始短信验证码登录...")
        
        try:
            # 导航到登录页
            await self.context_page.goto(
                "https://www.douban.com/accounts/login",
                wait_until="domcontentloaded",
                timeout=30000
            )
            await asyncio.sleep(2)
            
            # 确保选中短信登录标签
            sms_tab_selectors = [
                "xpath=//div[contains(text(), '短信登录')]",
                "xpath=//button[contains(text(), '短信登录')]",
                "xpath=//a[contains(text(), '短信登录')]",
            ]
            
            for selector in sms_tab_selectors:
                try:
                    element = await self.context_page.query_selector(selector)
                    if element:
                        await element.click()
                        await asyncio.sleep(1)
                        utils.logger.info("[DoubanLogin.login_by_sms] 点击短信登录标签")
                        break
                except Exception:
                    continue
            
            # 查找手机号输入框
            phone_input_selectors = [
                "input[placeholder*='手机']",
                "input[placeholder*='电话']",
                "input[type='tel']",
                "xpath=//input[@placeholder]",
            ]
            
            phone_input = None
            for selector in phone_input_selectors:
                try:
                    phone_input = await self.context_page.query_selector(selector)
                    if phone_input:
                        utils.logger.info(f"[DoubanLogin.login_by_sms] 找到手机号输入框")
                        break
                except Exception:
                    continue
            
            if not phone_input:
                utils.logger.error("[DoubanLogin.login_by_sms] 无法找到手机号输入框")
                return False
            
            # 输入手机号
            await phone_input.fill(self.login_phone)
            await asyncio.sleep(1)
            
            # 点击获取验证码按钮
            code_button_selectors = [
                "button:has-text('获取验证码')",
                "xpath=//button[contains(text(), '获取验证码')]",
                "xpath=//button[contains(text(), '获取')]",
            ]
            
            code_button = None
            for selector in code_button_selectors:
                try:
                    code_button = await self.context_page.query_selector(selector)
                    if code_button:
                        await code_button.click()
                        await asyncio.sleep(1)
                        utils.logger.info("[DoubanLogin.login_by_sms] 点击获取验证码按钮")
                        break
                except Exception:
                    continue
            
            # 等待用户输入验证码（从 Redis 或控制台）
            utils.logger.info("[DoubanLogin.login_by_sms] 等待验证码，请输入收到的短信验证码...")
            
            # 这里需要对接验证码接收服务
            # 简单起见，这里只是等待
            for i in range(120):
                await asyncio.sleep(1)
                
                # 检查是否已登录
                current_cookie = await self.browser_context.cookies()
                cookies_dict = {c["name"]: c["value"] for c in current_cookie}
                
                if cookies_dict.get("dbcl2"):
                    utils.logger.info("[DoubanLogin.login_by_sms] 检测到登录状态")
                    return True
            
            utils.logger.error("[DoubanLogin.login_by_sms] 验证码输入超时")
            return False
            
        except Exception as e:
            utils.logger.error(f"[DoubanLogin.login_by_sms] 短信登录异常: {e}")
            return False

    async def login_by_cookies(self):
        """使用 Cookie 登录豆瓣（增强版）"""
        utils.logger.info("[DoubanLogin.login_by_cookies] 开始 Cookie 登录...")
        
        try:
            if not config.COOKIES:
                utils.logger.error("[DoubanLogin.login_by_cookies] 未配置 COOKIES")
                return False
            
            # 解析 Cookie JSON
            try:
                cookies_list = eval(config.COOKIES)
            except Exception as e:
                utils.logger.error(f"[DoubanLogin.login_by_cookies] Cookie JSON 解析失败: {e}")
                return False
            
            # 规范化 Cookie 格式：确保每个 Cookie 都有 url 或 domain/path
            normalized_cookies = []
            for cookie in cookies_list:
                # 如果没有 url，则添加 domain 和 path（Playwright 要求）
                if "url" not in cookie:
                    if "domain" not in cookie:
                        cookie["domain"] = ".douban.com"  # 为豆瓣设置默认 domain
                    if "path" not in cookie:
                        cookie["path"] = "/"
                normalized_cookies.append(cookie)
            
            utils.logger.info(f"[DoubanLogin.login_by_cookies] 准备添加 {len(normalized_cookies)} 个 Cookie")
            
            # 添加 Cookie 到浏览器
            try:
                await self.browser_context.add_cookies(normalized_cookies)
                utils.logger.info("[DoubanLogin.login_by_cookies] Cookie 已添加到浏览器")
            except Exception as e:
                utils.logger.error(f"[DoubanLogin.login_by_cookies] 添加 Cookie 失败: {e}")
                return False
            
            # 访问豆瓣首页以应用 Cookie 并验证登录
            try:
                await self.context_page.goto("https://www.douban.com", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2)
            except Exception as e:
                utils.logger.warning(f"[DoubanLogin.login_by_cookies] 访问豆瓣首页超时: {e}")
            
            # 验证登录状态
            current_cookie = await self.browser_context.cookies()
            cookies_dict = {c["name"]: c["value"] for c in current_cookie}
            
            if cookies_dict.get("dbcl2"):
                utils.logger.info("[DoubanLogin.login_by_cookies] Cookie 登录成功，检测到有效 dbcl2")
                return True
            else:
                utils.logger.warning("[DoubanLogin.login_by_cookies] Cookie 登录状态未确定，dbcl2 未检测到，但继续尝试")
                # 即使没有 dbcl2，也不一定登录失败，继续尝试爬取
                return True
                
        except Exception as e:
            utils.logger.error(f"[DoubanLogin.login_by_cookies] Cookie 登录异常: {e}")
            return False

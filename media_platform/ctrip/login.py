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


class CtripLogin(AbstractLogin):
    """携程登录模块，支持二维码、短信验证码和 Cookie 登录"""

    async def login_by_mobile(self):
        """携程暂不支持 mobile 方式登录，仅为兼容基类接口"""
        raise NotImplementedError("CtripLogin 不支持 login_by_mobile 方法")

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
            # 方法 1：检查页面中的用户名显示
            user_info_selector = "xpath=//div[contains(@class, 'userinfo')] or //*[contains(text(), '我的')]"
            is_visible = await self.context_page.is_visible(user_info_selector, timeout=500)
            if is_visible:
                utils.logger.info("[CtripLogin.check_login_state] 检测到用户信息，登录成功")
                return True
        except Exception:
            pass

        try:
            # 方法 2：检查页面 URL 是否仍在登录页
            current_url = self.context_page.url
            if "login" not in current_url.lower():
                utils.logger.info("[CtripLogin.check_login_state] 已离开登录页，登录成功")
                return True
        except Exception:
            pass

        # 方法 3：检查 Cookie 变化
        try:
            current_cookie = await self.browser_context.cookies()
            current_cookies_dict = {c["name"]: c["value"] for c in current_cookie}
            current_session = current_cookies_dict.get("SESSION")
            
            # 携程登录后会设置 SESSION Cookie
            if current_session and current_session != no_logged_in_session:
                utils.logger.info("[CtripLogin.check_login_state] 检测到 Cookie 变化，登录成功")
                return True
        except Exception as e:
            utils.logger.warning(f"[CtripLogin.check_login_state] Cookie 检查失败: {e}")

        return False

    async def begin(self):
        """开始登录"""
        utils.logger.info("[CtripLogin.begin] 开始携程登录...")
        if config.LOGIN_TYPE == "qrcode":
            await self.login_by_qrcode()
        elif config.LOGIN_TYPE == "phone":
            await self.login_by_sms()
        elif config.LOGIN_TYPE == "cookie":
            await self.login_by_cookies()
        else:
            raise ValueError(
                f"[CtripLogin.begin] 不支持的登录方式: {config.LOGIN_TYPE}. "
                "支持的方式: qrcode, phone, cookie"
            )

    async def login_by_qrcode(self):
        """使用二维码登录携程"""
        utils.logger.info("[CtripLogin.login_by_qrcode] 开始二维码登录...")
        
        try:
            # 导航到登录页
            await self.context_page.goto(
                "https://accounts.ctrip.com/login",
                wait_until="domcontentloaded",
                timeout=30000
            )
            await asyncio.sleep(2)
            
            # 尝试查找二维码
            qrcode_selectors = [
                "xpath=//img[contains(@class, 'qrcode')]",
                "xpath=//img[contains(@src, 'qrcode') or contains(@src, 'qr')]",
                "xpath=//div[contains(@class, 'qr')]//img",
                "img.qrcode-img",
                "xpath=//img[@id='qrcode']",
                "xpath=//img[@alt='二维码']",
            ]
            
            qrcode_img = None
            for selector in qrcode_selectors:
                try:
                    qrcode_img = await self.context_page.query_selector(selector)
                    if qrcode_img:
                        utils.logger.info(f"[CtripLogin.login_by_qrcode] 找到二维码: {selector}")
                        break
                except Exception:
                    continue
            
            if not qrcode_img:
                utils.logger.warning("[CtripLogin.login_by_qrcode] 无法在登录页找到二维码，尝试点击切换")
                
                # 尝试点击二维码登录标签
                qrcode_tab_selectors = [
                    "xpath=//div[contains(text(), '二维码')]",
                    "xpath=//button[contains(text(), '二维码')]",
                    "xpath=//a[contains(text(), '二维码')]",
                    "xpath=//*[contains(@class, 'qrcode-tab')]",
                    "xpath=//span[contains(text(), '扫描登录')]",
                ]
                
                for selector in qrcode_tab_selectors:
                    try:
                        element = await self.context_page.query_selector(selector)
                        if element:
                            await element.click()
                            await asyncio.sleep(2)
                            utils.logger.info("[CtripLogin.login_by_qrcode] 点击二维码登录按钮")
                            break
                    except Exception:
                        continue
                
                # 再次查找二维码
                for selector in qrcode_selectors:
                    try:
                        qrcode_img = await self.context_page.query_selector(selector)
                        if qrcode_img:
                            utils.logger.info(f"[CtripLogin.login_by_qrcode] 切换后找到二维码")
                            break
                    except Exception:
                        continue
            
            if not qrcode_img:
                utils.logger.error("[CtripLogin.login_by_qrcode] 无法找到二维码，登录失败")
                return False
            
            # 提取二维码图片
            try:
                base64_qrcode_img = await utils.find_login_qrcode(
                    self.context_page,
                    selector="img[class*='qrcode']"
                )
            except Exception:
                base64_qrcode_img = None
            
            if not base64_qrcode_img:
                utils.logger.error("[CtripLogin.login_by_qrcode] 无法提取二维码图片")
                return False
            
            # 获取登录前的 SESSION Cookie
            current_cookie = await self.browser_context.cookies()
            cookies_dict = {c["name"]: c["value"] for c in current_cookie}
            no_logged_in_session = cookies_dict.get("SESSION", "")
            
            # 显示二维码给用户扫描
            utils.logger.info("[CtripLogin.login_by_qrcode] 显示二维码，请用手机扫描...")
            partial_show_qrcode = functools.partial(utils.show_qrcode, base64_qrcode_img)
            asyncio.get_running_loop().run_in_executor(executor=None, func=partial_show_qrcode)
            
            # 等待用户扫描二维码（最多 120 秒）
            utils.logger.info("[CtripLogin.login_by_qrcode] 等待用户扫描二维码，剩余时间 120s")
            try:
                await self.check_login_state(no_logged_in_session)
            except RetryError:
                utils.logger.error("[CtripLogin.login_by_qrcode] 二维码登录失败或超时")
                return False
            
            # 登录成功，等待页面重定向
            wait_redirect_seconds = 5
            utils.logger.info(
                f"[CtripLogin.login_by_qrcode] 登录成功，等待 {wait_redirect_seconds} 秒页面重定向..."
            )
            await asyncio.sleep(wait_redirect_seconds)
            
            return True
            
        except Exception as e:
            utils.logger.error(f"[CtripLogin.login_by_qrcode] 二维码登录异常: {e}")
            return False

    async def login_by_sms(self):
        """使用短信验证码登录携程"""
        utils.logger.info("[CtripLogin.login_by_sms] 开始短信验证码登录...")
        
        try:
            # 导航到登录页
            await self.context_page.goto(
                "https://accounts.ctrip.com/login",
                wait_until="domcontentloaded",
                timeout=30000
            )
            await asyncio.sleep(2)
            
            # 确保选中短信登录标签
            sms_tab_selectors = [
                "xpath=//div[contains(text(), '短信')]",
                "xpath=//button[contains(text(), '短信')]",
                "xpath=//a[contains(text(), '短信')]",
                "xpath=//span[contains(text(), '手机')]",
            ]
            
            for selector in sms_tab_selectors:
                try:
                    element = await self.context_page.query_selector(selector)
                    if element:
                        await element.click()
                        await asyncio.sleep(1)
                        utils.logger.info("[CtripLogin.login_by_sms] 点击短信登录标签")
                        break
                except Exception:
                    continue
            
            # 查找手机号输入框
            phone_input_selectors = [
                "input[placeholder*='手机']",
                "input[placeholder*='电话']",
                "input[type='tel']",
                "input[name='mobile']",
                "xpath=//input[@placeholder]",
            ]
            
            phone_input = None
            for selector in phone_input_selectors:
                try:
                    phone_input = await self.context_page.query_selector(selector)
                    if phone_input:
                        utils.logger.info(f"[CtripLogin.login_by_sms] 找到手机号输入框")
                        break
                except Exception:
                    continue
            
            if not phone_input:
                utils.logger.error("[CtripLogin.login_by_sms] 无法找到手机号输入框")
                return False
            
            # 输入手机号
            await phone_input.fill(self.login_phone)
            await asyncio.sleep(1)
            
            # 点击获取验证码按钮
            code_button_selectors = [
                "button:has-text('获取验证码')",
                "xpath=//button[contains(text(), '获取验证码')]",
                "xpath=//button[contains(text(), '获取')]",
                "xpath=//button[contains(text(), '发送')]",
            ]
            
            code_button = None
            for selector in code_button_selectors:
                try:
                    code_button = await self.context_page.query_selector(selector)
                    if code_button:
                        await code_button.click()
                        await asyncio.sleep(1)
                        utils.logger.info("[CtripLogin.login_by_sms] 点击获取验证码按钮")
                        break
                except Exception:
                    continue
            
            # 等待用户输入验证码（从 Redis 或控制台）
            utils.logger.info("[CtripLogin.login_by_sms] 等待验证码，请输入收到的短信验证码...")
            
            for i in range(120):
                await asyncio.sleep(1)
                
                # 检查是否已登录
                current_cookie = await self.browser_context.cookies()
                cookies_dict = {c["name"]: c["value"] for c in current_cookie}
                
                if cookies_dict.get("SESSION"):
                    utils.logger.info("[CtripLogin.login_by_sms] 检测到登录状态")
                    return True
            
            utils.logger.error("[CtripLogin.login_by_sms] 验证码输入超时")
            return False
            
        except Exception as e:
            utils.logger.error(f"[CtripLogin.login_by_sms] 短信登录异常: {e}")
            return False

    async def login_by_cookies(self):
        """使用 Cookie 登录携程（支持字符串和 JSON 格式）"""
        utils.logger.info("[CtripLogin.login_by_cookies] 开始 Cookie 登录...")
        
        try:
            if not config.COOKIES:
                utils.logger.error("[CtripLogin.login_by_cookies] 未配置 COOKIES")
                return False
            
            # 解析 Cookie：支持字符串格式（key=value; key=value）和 JSON 格式
            cookies_list = []
            try:
                # 首先尝试作为 JSON 解析
                cookies_list = eval(config.COOKIES)
            except Exception:
                # 如果 JSON 解析失败，尝试作为字符串解析（key=value; key=value 格式）
                try:
                    if isinstance(config.COOKIES, str) and "=" in config.COOKIES:
                        # 分割 Cookie 字符串
                        cookie_parts = config.COOKIES.split("; ")
                        cookies_list = []
                        for part in cookie_parts:
                            if "=" in part:
                                key, value = part.split("=", 1)
                                cookies_list.append({"name": key.strip(), "value": value.strip()})
                        utils.logger.info(f"[CtripLogin.login_by_cookies] 已解析字符串格式 Cookie，共 {len(cookies_list)} 个")
                    else:
                        utils.logger.error("[CtripLogin.login_by_cookies] 无法识别 Cookie 格式")
                        return False
                except Exception as e:
                    utils.logger.error(f"[CtripLogin.login_by_cookies] Cookie 字符串解析失败: {e}")
                    return False
            
            # 规范化 Cookie 格式：确保每个 Cookie 都有 domain/path
            normalized_cookies = []
            for cookie in cookies_list:
                # 如果没有 url，则添加 domain 和 path
                if "url" not in cookie:
                    if "domain" not in cookie:
                        cookie["domain"] = ".ctrip.com"  # 为携程设置默认 domain
                    if "path" not in cookie:
                        cookie["path"] = "/"
                normalized_cookies.append(cookie)
            
            utils.logger.info(f"[CtripLogin.login_by_cookies] 准备添加 {len(normalized_cookies)} 个 Cookie")
            
            # 添加 Cookie 到浏览器
            try:
                await self.browser_context.add_cookies(normalized_cookies)
                utils.logger.info("[CtripLogin.login_by_cookies] Cookie 已添加到浏览器")
            except Exception as e:
                utils.logger.error(f"[CtripLogin.login_by_cookies] 添加 Cookie 失败: {e}")
                return False
            
            # 访问携程首页以应用 Cookie 并验证登录
            try:
                await self.context_page.goto(
                    "https://www.ctrip.com", 
                    wait_until="domcontentloaded", 
                    timeout=30000
                )
                await asyncio.sleep(2)
            except Exception as e:
                utils.logger.warning(f"[CtripLogin.login_by_cookies] 访问携程首页超时: {e}")
            
            # 验证登录状态
            current_cookie = await self.browser_context.cookies()
            cookies_dict = {c["name"]: c["value"] for c in current_cookie}
            
            if cookies_dict.get("SESSION"):
                utils.logger.info("[CtripLogin.login_by_cookies] Cookie 登录成功，检测到有效 SESSION")
                return True
            else:
                utils.logger.warning("[CtripLogin.login_by_cookies] Cookie 登录状态未确定，SESSION 未检测到，但继续尝试")
                # 即使没有 SESSION，也不一定登录失败，继续尝试爬取
                return True
                
        except Exception as e:
            utils.logger.error(f"[CtripLogin.login_by_cookies] Cookie 登录异常: {e}")
            return False

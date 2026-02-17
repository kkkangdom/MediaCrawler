# � 豆瓣爬虫 - MediaCrawler 定制版

这是基于 **[MediaCrawler](https://github.com/NanmiCoder/MediaCrawler)** 项目的定制版本，主要专注于豆瓣平台的爬虫功能开发。

## 🔗 原项目链接

- **原项目地址**：[NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler)
- **原项目介绍**：一个功能强大的多平台自媒体数据采集工具，支持小红书、抖音、快手、B站、微博、贴吧、知乎等主流平台

---

## 🎯 项目现状

### ✅ 已完成：豆瓣爬虫功能

本项目成功实现了**豆瓣日记爬虫**的完整功能，包括：

#### 📚 核心功能
- ✅ **关键词搜索**：搜索豆瓣日记分类下的相关内容
- ✅ **完整内容提取**：提取日记完整内容（支持 4000+ 字符）
- ✅ **Cookie 认证登录**：支持 Cookie 方式登录，无需扫码
- ✅ **媒体下载**：支持图片和视频资源下载
- ✅ **数据导出**：支持 Excel 和 JSON 格式导出

#### 📊 技术细节
| 功能 | 说明 | 状态 |
|------|------|------|
| 日记搜索 | cat=1015 分类搜索，支持关键词过滤 | ✅ |
| 内容提取 | 通过 XPath 提取完整日记内容 | ✅ |
| Cookie 登录 | Session 方式认证，自动处理重定向 | ✅ |
| 图片下载 | 支持异步下载日记中的图片 | ✅ |
| 视频下载 | 支持视频资源下载 | ✅ |
| 数据去重 | 内存级去重，避免重复爬取 | ✅ |
| Excel 导出 | 支持导出到 Excel 格式 | ✅ |
| JSON 导出 | 支持导出到 JSON 格式 | ✅ |

### 🚀 快速使用豆瓣爬虫

#### 1️⃣ 环境准备

```bash
# 进入项目目录
cd MediaCrawler

# 安装依赖
uv sync

# 安装浏览器驱动
uv run playwright install
```

#### 2️⃣ 配置 Cookie

在 `config/base_config.py` 中配置：

```python
PLATFORM = "douban"
KEYWORDS = "生活"  # 搜索的日记关键词
LOGIN_TYPE = "cookie"
COOKIES = "bid=xxx; SESSION=xxx; ..."  # 从浏览器复制的 Cookie
```

**如何获取 Cookie：**
1. 打开浏览器访问 https://www.douban.com
2. 按 F12 打开开发者工具
3. 进入 Application → Cookies
4. 复制所有 Cookie 值（name=value; name=value; ...）
5. 粘贴到配置文件中

#### 3️⃣ 运行爬虫

```bash
# 启动豆瓣日记爬虫
uv run main.py --platform douban --lt cookie --type search

# 或使用配置文件中的设置
uv run main.py
```

#### 4️⃣ 查看结果

爬取的数据会保存到 `data/douban/` 文件夹：
- `日记关键词_reviews.xlsx` - Excel 格式
- `日记关键词_reviews.json` - JSON 格式
- 下载的图片和视频会保存在相应文件夹

### ⚙️ 配置选项说明

在 `config/base_config.py` 中可以配置：

```python
# 搜索关键词（支持多个，用逗号分隔）
KEYWORDS = "生活,旅游,美食"

# 爬取页数
CRAWLER_MAX_PAGES = 5  # 最多爬取 5 页

# 每页爬取数量
CRAWLER_MAX_NOTES_COUNT = 500

# 并发数
MAX_CONCURRENCY_NUM = 2

# 数据保存格式
SAVE_DATA_OPTION = "excel"  # excel 或 json

# 是否下载媒体（图片/视频）
ENABLE_GET_MEIDAS = True

# Cookie 登录
LOGIN_TYPE = "cookie"
COOKIES = "..."
```

### 📚 详细文档

详细的豆瓣爬虫使用指南、Cookie 获取方法等，请查看 `docs/` 文件夹中的文档：
- `docs/Douban_Quick_Start.md` - 快速开始指南
- `docs/Cookie_Getting_Guide.md` - Cookie 获取详解
- `docs/完整豆瓣爬虫使用文档.md` - 完整功能文档

---

## ⚠️ 已完成但未解决的功能

### 🔴 携程爬虫（完成度：80%）

**进度说明：**
- ✅ 代码框架完成
- ✅ Cookie 登录机制实现
- ✅ 反爬虫绕过逻辑添加
- ✅ 代理 IP 集成
- ❌ **但仍无法绕过携程的反爬虫机制**

**状态：** 已完成大部分工作，但由于携程的反爬虫防护措施非常强硬（CDN + WAF + 设备指纹识别），目前暂未找到可行的绕过方案。

**相关代码位置：**
- `media_platform/ctrip/` - 携程爬虫实现
- `config/base_config.py` - 配置文件

如果对携程爬虫感兴趣，可以查看相关代码和文档。

---

## 🔗 其他平台爬虫

如果你需要爬取以下平台的内容，请查看**原 MediaCrawler 项目**的完整文档：

- 🔴 **小红书 (XHS)** - 完整支持
- 🎵 **抖音 (Douyin)** - 完整支持
- 🎬 **快手 (Kuaishou)** - 完整支持
- 📺 **B 站 (Bilibili)** - 完整支持
- 👥 **微博 (Weibo)** - 完整支持
- 📝 **贴吧 (Tieba)** - 完整支持
- 💡 **知乎 (Zhihu)** - 完整支持

**原项目地址：** [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler)



<strong>MediaCrawlerPro 重磅发布！开源不易，欢迎订阅支持</strong>

> 专注于学习成熟项目的架构设计，不仅仅是爬虫技术，Pro 版本的代码设计思路同样值得深入学习！

[MediaCrawlerPro](https://github.com/MediaCrawlerPro) 相较于开源版本的核心优势：

#### 🎯 核心功能升级
- ✅ **自媒体内容拆解Agent**（新增功能）
- ✅ **断点续爬功能**（重点特性）
- ✅ **多账号 + IP代理池支持**（重点特性）
- ✅ **去除 Playwright 依赖**，使用更简单
- ✅ **完整 Linux 环境支持**

#### 🏗️ 架构设计优化
- ✅ **代码重构优化**，更易读易维护（解耦 JS 签名逻辑）
- ✅ **企业级代码质量**，适合构建大型爬虫项目
- ✅ **完美架构设计**，高扩展性，源码学习价值更大

#### 🎁 额外功能
- ✅ **自媒体视频下载器桌面端**（适合学习全栈开发）
- ✅ **多平台首页信息流推荐**（HomeFeed）
- [ ] **基于评论分析AI Agent正在开发中 🚀🚀**

点击查看：[MediaCrawlerPro 项目主页](https://github.com/MediaCrawlerPro) 更多介绍



## 🚀 快速开始

> 💡 **如果这个项目对您有帮助，请给个 ⭐ Star 支持一下！**

## 📋 前置依赖

### 🚀 uv 安装（推荐）

在进行下一步操作之前，请确保电脑上已经安装了 uv：

- **安装地址**：[uv 官方安装指南](https://docs.astral.sh/uv/getting-started/installation)
- **验证安装**：终端输入命令 `uv --version`，如果正常显示版本号，证明已经安装成功
- **推荐理由**：uv 是目前最强的 Python 包管理工具，速度快、依赖解析准确

### 🟢 Node.js 安装

项目依赖 Node.js，请前往官网下载安装：

- **下载地址**：https://nodejs.org/en/download/
- **版本要求**：>= 16.0.0

### 📦 Python 包安装

```shell
# 进入项目目录
cd MediaCrawler

# 使用 uv sync 命令来保证 python 版本和相关依赖包的一致性
uv sync
```

### 🌐 浏览器驱动安装

```shell
# 安装浏览器驱动
uv run playwright install
```

## 🚀 运行爬虫程序

```shell
# 在 config/base_config.py 查看配置项目功能，写的有中文注释

# 从配置文件中读取关键词搜索相关的帖子并爬取帖子信息与评论
uv run main.py --platform xhs --lt qrcode --type search

# 从配置文件中读取指定的帖子ID列表获取指定帖子的信息与评论信息
uv run main.py --platform xhs --lt qrcode --type detail

# 打开对应APP扫二维码登录

# 其他平台爬虫使用示例，执行下面的命令查看
uv run main.py --help
```

<details>
<summary>🖥️ <strong>WebUI 可视化操作界面</strong></summary>

MediaCrawler 提供了基于 Web 的可视化操作界面，无需命令行也能轻松使用爬虫功能。

#### 启动 WebUI 服务

```shell
# 启动 API 服务器（默认端口 8080）
uv run uvicorn api.main:app --port 8080 --reload

# 或者使用模块方式启动
uv run python -m api.main
```

启动成功后，访问 `http://localhost:8080` 即可打开 WebUI 界面。

#### WebUI 功能特性

- 可视化配置爬虫参数（平台、登录方式、爬取类型等）
- 实时查看爬虫运行状态和日志
- 数据预览和导出

#### 界面预览

<img src="docs/static/images/img_8.png" alt="WebUI 界面预览">

</details>

<details>
<summary>🔗 <strong>使用 Python 原生 venv 管理环境（不推荐）</strong></summary>

#### 创建并激活 Python 虚拟环境

> 如果是爬取抖音和知乎，需要提前安装 nodejs 环境，版本大于等于：`16` 即可

```shell
# 进入项目根目录
cd MediaCrawler

# 创建虚拟环境
# 我的 python 版本是：3.11 requirements.txt 中的库是基于这个版本的
# 如果是其他 python 版本，可能 requirements.txt 中的库不兼容，需自行解决
python -m venv venv

# macOS & Linux 激活虚拟环境
source venv/bin/activate

# Windows 激活虚拟环境
venv\Scripts\activate
```

#### 安装依赖库

```shell
pip install -r requirements.txt
```

#### 安装 playwright 浏览器驱动

```shell
playwright install
```

#### 运行爬虫程序（原生环境）

```shell
# 项目默认是没有开启评论爬取模式，如需评论请在 config/base_config.py 中的 ENABLE_GET_COMMENTS 变量修改
# 一些其他支持项，也可以在 config/base_config.py 查看功能，写的有中文注释

# 从配置文件中读取关键词搜索相关的帖子并爬取帖子信息与评论
python main.py --platform xhs --lt qrcode --type search

# 从配置文件中读取指定的帖子ID列表获取指定帖子的信息与评论信息
python main.py --platform xhs --lt qrcode --type detail

# 打开对应APP扫二维码登录

# 其他平台爬虫使用示例，执行下面的命令查看
python main.py --help
```

</details>


## 💾 数据保存

MediaCrawler 支持多种数据存储方式，包括 CSV、JSON、Excel、SQLite 和 MySQL 数据库。

📖 **详细使用说明请查看：[数据存储指南](docs/data_storage_guide.md)**


[🚀 MediaCrawlerPro 重磅发布 🚀！更多的功能，更好的架构设计！开源不易，欢迎订阅支持！](https://github.com/MediaCrawlerPro)


## 💬 交流群组
- **微信交流群**：[点击加入](https://nanmicoder.github.io/MediaCrawler/%E5%BE%AE%E4%BF%A1%E4%BA%A4%E6%B5%81%E7%BE%A4.html)
- **B站账号**：[关注我](https://space.bilibili.com/434377496)，分享AI与爬虫技术知识


## 💰 赞助商展示

<a href="https://tikhub.io/?utm_source=github.com/NanmiCoder/MediaCrawler&utm_medium=marketing_social&utm_campaign=retargeting&utm_content=carousel_ad">
<img width="500" src="docs/static/images/tikhub_banner_zh.png">
<br>
TikHub.io 提供 900+ 高稳定性数据接口，覆盖 TK、DY、XHS、Y2B、Ins、X 等 14+ 海内外主流平台，支持用户、内容、商品、评论等多维度公开数据 API，并配套 4000 万+ 已清洗结构化数据集，使用邀请码 <code>cfzyejV9</code> 注册并充值，即可额外获得 $2 赠送额度。
</a>

---

<a href="https://www.thordata.com/?ls=github&lk=mediacrawler">
<img width="500" src="docs/static/images/Thordata.png">
<br>
Thordata：可靠且经济高效的代理服务提供商。为企业和开发者提供稳定、高效且合规的全球代理 IP 服务。立即注册，赠送1GB住宅代理免费试用和2000次serp-api调用。
</a>
<br>
<a href="https://www.thordata.com/products/residential-proxies/?ls=github&lk=mediacrawler">【住宅代理】</a> | <a href="https://www.thordata.com/products/web-scraper/?ls=github&lk=mediacrawler">【serp-api】</a>


## 🤝 成为赞助者

成为赞助者，可以将您的产品展示在这里，每天获得大量曝光！

**联系方式**：
- 微信：`relakkes`
- 邮箱：`relakkes@gmail.com`
---

## 📚 其他
- **常见问题**：[MediaCrawler 完整文档](https://nanmicoder.github.io/MediaCrawler/)
- **爬虫入门教程**：[CrawlerTutorial 免费教程](https://github.com/NanmiCoder/CrawlerTutorial)
- **新闻爬虫开源项目**：[NewsCrawlerCollection](https://github.com/NanmiCoder/NewsCrawlerCollection)


## ⭐ Star 趋势图

如果这个项目对您有帮助，请给个 ⭐ Star 支持一下，让更多的人看到 MediaCrawler！

[![Star History Chart](https://api.star-history.com/svg?repos=NanmiCoder/MediaCrawler&type=Date)](https://star-history.com/#NanmiCoder/MediaCrawler&Date)


## 📚 参考

- **小红书签名仓库**：[Cloxl 的 xhs 签名仓库](https://github.com/Cloxl/xhshow)
- **小红书客户端**：[ReaJason 的 xhs 仓库](https://github.com/ReaJason/xhs)
- **短信转发**：[SmsForwarder 参考仓库](https://github.com/pppscn/SmsForwarder)
- **内网穿透工具**：[ngrok 官方文档](https://ngrok.com/docs/)


# 免责声明
<div id="disclaimer"> 

## 1. 项目目的与性质
本项目（以下简称“本项目”）是作为一个技术研究与学习工具而创建的，旨在探索和学习网络数据采集技术。本项目专注于自媒体平台的数据爬取技术研究，旨在提供给学习者和研究者作为技术交流之用。

## 2. 法律合规性声明
本项目开发者（以下简称“开发者”）郑重提醒用户在下载、安装和使用本项目时，严格遵守中华人民共和国相关法律法规，包括但不限于《中华人民共和国网络安全法》、《中华人民共和国反间谍法》等所有适用的国家法律和政策。用户应自行承担一切因使用本项目而可能引起的法律责任。

## 3. 使用目的限制
本项目严禁用于任何非法目的或非学习、非研究的商业行为。本项目不得用于任何形式的非法侵入他人计算机系统，不得用于任何侵犯他人知识产权或其他合法权益的行为。用户应保证其使用本项目的目的纯属个人学习和技术研究，不得用于任何形式的非法活动。

## 4. 免责声明
开发者已尽最大努力确保本项目的正当性及安全性，但不对用户使用本项目可能引起的任何形式的直接或间接损失承担责任。包括但不限于由于使用本项目而导致的任何数据丢失、设备损坏、法律诉讼等。

## 5. 知识产权声明
本项目的知识产权归开发者所有。本项目受到著作权法和国际著作权条约以及其他知识产权法律和条约的保护。用户在遵守本声明及相关法律法规的前提下，可以下载和使用本项目。

## 6. 最终解释权
关于本项目的最终解释权归开发者所有。开发者保留随时更改或更新本免责声明的权利，恕不另行通知。
</div>

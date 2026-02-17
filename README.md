# 📖 豆瓣爬虫 - MediaCrawler 定制版

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

---

## 📜 免责声明

本项目是作为一个技术研究与学习工具而创建的，仅供学习和研究之用。

**重要声明：**
- ⚠️ 本项目严禁用于任何非法目的或商业行为
- ⚠️ 使用本项目时应遵守目标平台的使用条款和 robots.txt 规则
- ⚠️ 不得进行大规模爬取或对平台造成运营干扰
- ⚠️ 应合理控制请求频率，避免给目标平台带来不必要的负担
- ⚠️ 不得用于任何非法或不当的用途

用户应自行承担使用本项目而可能引起的一切法律责任。开发者不对用户使用本项目可能引起的任何形式的直接或间接损失承担责任。

---

## 📞 联系与反馈

如有问题或建议，欢迎提交 Issue 或 Pull Request。

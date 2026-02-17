# 豆瓣爬虫完整使用指南

## 📌 概述

本文档介绍如何使用 MediaCrawler 的豆瓣爬虫功能。该爬虫支持：

- ✅ **日记内容爬取**：搜索豆瓣日记分类，并提取完整的文章内容
- ✅ **图片下载**：自动下载所有文章中的图片
- ✅ **灵活导出**：支持 JSON 和 Excel 两种格式
- ✅ **反爬虫机制**：内置 Cookie 登录和隐身脚本，有效规避反爬虫检测
- ✅ **代理支持**：支持代理 IP 池，可配置多个代理

---

## 🚀 快速开始

### 1. 配置账户信息

编辑 `config/base_config.py`，配置豆瓣 Cookie：

```python
# 豆瓣平台
PLATFORM = "douban"
KEYWORDS = "愚园路"  # 搜索关键词
LOGIN_TYPE = "cookie"  # 使用 Cookie 登录

# 豆瓣 Cookie 配置 (从浏览器获取)
COOKIES = {
    "bid": "your_bid_here",           # 从浏览器 Cookie 中获取 bid
    "dbcl2": "293236485:your_token"   # 从浏览器 Cookie 中获取 dbcl2
}

# 爬取配置
CRAWLER_TYPE = "search"           # 搜索模式
CRAWLER_MAX_PAGES = 5             # 爬取页数 (每页20条)
ENABLE_GET_MEIDAS = True          # 是否下载图片
ENABLE_GET_COMMENTS = False       # 是否爬取评论
SAVE_DATA_OPTION = "excel"        # 数据保存格式: "json" 或 "excel"
```

### 2. 获取 Cookie

**方法 1：使用浏览器开发者工具**

1. 打开 https://www.douban.com/
2. 登录你的豆瓣账号
3. 打开浏览器开发者工具 (F12 或 Command+Option+I)
4. 切换到 **Storage** 或 **Application** 标签
5. 在 Cookies 中找到 `bid` 和 `dbcl2`，复制到配置文件

**方法 2：使用浏览器控制台**

```javascript
// 在浏览器控制台执行以下代码
console.log(document.cookie);
```

### 3. 运行爬虫

```bash
# 方法 1：使用 uv 运行
uv run main.py --platform douban --lt cookie --type search

# 方法 2：直接使用 Python
python main.py --platform douban --lt cookie --type search

# 方法 3：指定关键词
python main.py --platform douban --keywords "愚园路" --lt cookie --type search
```

### 4. 查看结果

爬取的数据保存在：

```
data/douban/
├── _posts.xlsx          # Excel 格式的帖子数据
├── _posts.json          # JSON 格式的帖子数据（可选）
└── images/              # 下载的图片文件
    ├── post_id_1/
    ├── post_id_2/
    └── ...
```

---

## 📊 数据格式说明

### Excel 导出格式

| 列号 | 列名 | 说明 | 示例 |
|------|------|------|------|
| A | Post ID | 帖子唯一ID | `801470947` |
| B | Title | 帖子标题 | `撕掉网红标签，一起重新认识一下上海愚园路吧！` |
| C | Content | 完整文章内容 | `要比城市里好逛的路，上海...` |
| D | Author | 作者昵称 | `罐头里的咸鱼` |
| E | Created Time | 发布时间 | `2021-04-28 21:54:50` |
| F | Likes | 点赞数 | `150` |
| G | Replies | 评论数 | `25` |
| H | Images | 图片URL列表 | `[url1, url2, ...]` |

### JSON 导出格式

```json
{
  "posts": [
    {
      "post_id": "801470947",
      "title": "撕掉网红标签，一起重新认识一下上海愚园路吧！",
      "content": "要比城市里好逛的路，上海肯定是不会输的。压马路圣地...",
      "author": "罐头里的咸鱼",
      "created_time": "2021-04-28 21:54:50",
      "likes": 150,
      "replies": 25,
      "images": [
        "https://img1.doubanio.com/view/note/large/public/p81539629.jpg",
        "https://img2.doubanio.com/view/note/large/public/p81539630.jpg"
      ]
    }
  ]
}
```

---

## ⚙️ 配置参数详解

### 基础配置

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `PLATFORM` | str | 爬虫平台 | `"douban"` |
| `KEYWORDS` | str | 搜索关键词 | `"愚园路"` |
| `LOGIN_TYPE` | str | 登录方式 | `"cookie"` |
| `COOKIES` | dict | 浏览器 Cookie | `{}` |

### 爬取配置

| 参数 | 类型 | 说明 | 默认值 | 建议值 |
|------|------|------|--------|--------|
| `CRAWLER_TYPE` | str | 爬虫类型 | `"search"` | `"search"` |
| `CRAWLER_MAX_PAGES` | int | 爬取页数 | `1` | `2-5` |
| `ENABLE_GET_MEIDAS` | bool | 是否下载图片 | `True` | `True` |
| `ENABLE_GET_COMMENTS` | bool | 是否爬取评论 | `False` | `False` |

### 数据导出配置

| 参数 | 类型 | 说明 | 选项 |
|------|------|------|------|
| `SAVE_DATA_OPTION` | str | 数据保存格式 | `"json"` / `"excel"` |

### 代理配置

| 参数 | 类型 | 说明 |
|------|------|------|
| `ENABLE_IP_PROXY` | bool | 是否启用代理 IP |
| `IP_PROXY_POOL_COUNT` | int | 代理池数量 |
| `PROXY_PROVIDER_NAME` | str | 代理提供商 |

---

## 🔍 搜索功能详解

### 日记搜索

豆瓣爬虫默认搜索**日记分类**（diary category），这是最推荐的搜索方式。

```bash
# 搜索关键词"愚园路"的所有日记
python main.py --keywords "愚园路"
```

搜索会自动：
1. 构建搜索 URL：`https://www.douban.com/search?q={keyword}&cat=1015`
2. 处理 URL 编码
3. 解析搜索结果页面
4. 提取帖子列表
5. 逐一爬取每篇日记的完整内容

### 搜索结果

每页返回约 **20 条结果**，可通过 `CRAWLER_MAX_PAGES` 配置爬取页数：

```python
CRAWLER_MAX_PAGES = 1   # 爬取 20 条
CRAWLER_MAX_PAGES = 5   # 爬取 100 条
CRAWLER_MAX_PAGES = 10  # 爬取 200 条
```

---

## 📸 图片下载配置

### 启用图片下载

```python
ENABLE_GET_MEIDAS = True  # 启用图片下载
```

### 图片保存位置

```
data/douban/images/
├── 801470947/           # 按 post_id 建立文件夹
│   ├── img_1.jpg
│   ├── img_2.jpg
│   └── ...
├── 789654321/
│   └── ...
```

### 图片 URL 格式

豆瓣日记中的图片 URL 通常为：

```
https://img1.doubanio.com/view/note/large/public/p81539629.jpg
https://img2.doubanio.com/view/note/large/public/p81539630.webp
```

爬虫会自动过滤和下载所有有效的图片。

---

## 🛡️ 反爬虫机制

### Cookie 登录

豆瓣爬虫使用 **Cookie 登录方式**，优势：

- ✅ 无需手动扫描二维码
- ✅ 登录稳定可靠
- ✅ 不容易被风控
- ✅ 支持批量爬取

### 隐身脚本

爬虫内置了 Puppeteer 隐身脚本（`/libs/stealth.min.js`），可以：

- 隐藏 `webdriver` 标记
- 伪装成正常浏览器
- 绕过反爬虫检测

### 请求频率控制

```python
# 在 core.py 中的相关部分
await asyncio.sleep(random.uniform(2, 5))  # 随机延迟 2-5 秒
```

建议：
- 单次爬取不超过 **100 条** 帖子
- 两次爬取间隔 **1 小时以上**
- 避免在高峰时段爬取

---

## ❌ 常见问题

### 问题 1：Cookie 过期

**症状**：爬虫报错 `401 Unauthorized` 或被重定向到登录页

**解决方案**：
1. 重新在浏览器中登录豆瓣
2. 重新获取最新的 `bid` 和 `dbcl2`
3. 更新配置文件中的 Cookie

```bash
# 快速重新登录
# 1. 清除浏览器 Cookie
# 2. 访问 https://www.douban.com
# 3. 重新登录
# 4. 复制新的 Cookie
```

### 问题 2：内容为空

**症状**：Excel 文件中 `Content` 列为空

**解决方案**：
- 检查 HTML 结构是否变更
- 查看日志输出中的 `Content length` 信息
- 尝试手动访问某条帖子 URL 验证内容

### 问题 3：图片下载失败

**症状**：`images/` 文件夹为空或缺少部分图片

**解决方案**：
- 检查网络连接
- 检查磁盘空间
- 查看日志中的下载错误信息
- 尝试使用代理 IP

### 问题 4：被风控或限流

**症状**：频繁报错、返回 429 Too Many Requests、或被临时封禁

**解决方案**：
1. 停止爬取，等待 1-2 小时
2. 减少 `CRAWLER_MAX_PAGES`
3. 增加请求间隔：
   ```python
   await asyncio.sleep(random.uniform(5, 10))  # 改为 5-10 秒
   ```
4. 启用代理 IP：
   ```python
   ENABLE_IP_PROXY = True
   ```

---

## 🔧 高级用法

### 使用代理 IP

```python
# config/base_config.py
ENABLE_IP_PROXY = True
IP_PROXY_POOL_COUNT = 5
PROXY_PROVIDER_NAME = "kuaidaili"  # 或其他代理商
```

### 修改搜索策略

编辑 `media_platform/douban/core.py` 中的 `search()` 方法：

```python
# 修改搜索关键词
search_url = f"https://www.douban.com/search?q={quote(keyword)}&cat=1015"

# cat 参数含义：
# cat=1000 - 全部
# cat=1015 - 日记
# cat=1009 - 讨论
```

### 自定义数据提取

编辑 `media_platform/douban/help.py` 中的 `extract_post_detail()` 方法来修改数据提取逻辑。

---

## 📝 示例使用场景

### 场景 1：搜索特定地点的旅游笔记

```python
# config/base_config.py
PLATFORM = "douban"
KEYWORDS = "京都旅游"
CRAWLER_MAX_PAGES = 3
ENABLE_GET_MEIDAS = True
SAVE_DATA_OPTION = "excel"
```

```bash
python main.py
```

**结果**：`data/douban/_posts.xlsx` 包含约 60 条京都旅游日记及图片

### 场景 2：批量爬取多个关键词

```bash
# 创建脚本 batch_crawl.sh
#!/bin/bash
keywords=("愚园路" "安福路" "武康路")
for kw in "${keywords[@]}"
do
  echo "爬取关键词: $kw"
  python main.py --keywords "$kw"
  sleep 3600  # 等待 1 小时
done
```

### 场景 3：只爬取内容，不下载图片

```python
# config/base_config.py
ENABLE_GET_MEIDAS = False
SAVE_DATA_OPTION = "json"
```

---

## 📌 注意事项

### 法律与合规

1. **遵守平台条款**：使用本爬虫前请阅读豆瓣[用户协议](https://www.douban.com/about/legal)
2. **控制爬取频率**：避免对豆瓣服务器造成压力
3. **尊重用户隐私**：不得用于商业目的或骚扰用户
4. **合理使用数据**：下载的数据仅供个人研究和学习使用

### 技术建议

1. **定期维护 Cookie**：Cookie 过期后需要重新更新
2. **监控爬虫日志**：及时发现和解决问题
3. **备份重要数据**：定期备份爬取的数据
4. **测试小范围**：先测试 1 页数据，验证无误后再大规模爬取

---

## 📞 获取帮助

如遇到问题，请：

1. 查看日志输出（`logs/` 目录）
2. 检查配置文件是否正确
3. 查看本文档的"常见问题"部分
4. 提交 Issue 到 GitHub 仓库

---

## 📚 相关资源

- [豆瓣网站](https://www.douban.com/)
- [MediaCrawler GitHub](https://github.com/NanmiCoder/MediaCrawler)
- [项目架构文档](./项目架构文档.md)
- [Excel 导出指南](./excel_export_guide.md)

---

## 更新日志

### v1.0（2026-02-17）

- ✅ 完成豆瓣日记搜索功能
- ✅ 实现完整内容提取（4000+ 字符）
- ✅ 支持图片自动下载
- ✅ 提供 JSON 和 Excel 双格式导出
- ✅ 集成 Cookie 登录和反爬虫机制
- ✅ 编写完整使用文档

---

最后更新：2026-02-17

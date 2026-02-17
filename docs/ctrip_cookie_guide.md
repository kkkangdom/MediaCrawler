# 携程爬虫 Cookie 获取指南

## 📋 目录

1. [为什么需要 Cookie](#为什么需要-cookie)
2. [Cookie 获取步骤](#cookie-获取步骤)
3. [Cookie 格式说明](#cookie-格式说明)
4. [配置 Cookie](#配置-cookie)
5. [验证 Cookie 有效性](#验证-cookie-有效性)
6. [常见问题](#常见问题)

---

## 为什么需要 Cookie

携程网站有反爬虫机制，直接访问会被识别为爬虫并返回空白页面。通过使用真实用户的 Cookie，我们可以：

- ✅ 绕过反爬虫检测
- ✅ 获取完整的网页内容
- ✅ 提高数据抓取成功率
- ✅ 避免 IP 被封禁

---

## Cookie 获取步骤

### 🖥️ 方法 1：使用 Chrome/Chromium 浏览器（推荐）

#### 步骤 1：打开携程网站

1. 打开 Chrome 或 Edge 浏览器
2. 访问 https://www.ctrip.com
3. 确保页面完全加载

```
浏览器地址栏输入：https://www.ctrip.com
按 Enter 键访问
```

#### 步骤 2：登录携程账户（可选但推荐）

1. 点击页面右上角 **"登录/注册"**
2. 选择登录方式：
   - 手机号码 + 密码
   - 邮箱 + 密码
   - 微信/支付宝扫码

3. 完成登录和任何验证

```
未登录也可以爬取，但登录会获得更多权限和内容
```

#### 步骤 3：打开开发者工具

**Windows/Linux:**
```
按 F12 或 右键 → 检查元素
```

**macOS:**
```
按 Cmd + Option + I 或 右键 → 检查元素
```

你会看到开发者工具窗口打开。

#### 步骤 4：切换到 Network 或 Application 标签

**方法 A：使用 Network 标签（更直接）**

1. 点击开发者工具顶部的 **Network** 标签
2. 刷新页面（按 F5 或 Cmd+R）
3. 等待页面加载完成
4. 在 Network 列表中点击任意一个请求（如 `index.html` 或 `ctrip.com`）
5. 在右侧面板找到 **Request Headers** 部分
6. 找到 **Cookie** 字段

```
Network 标签显示所有网络请求
↓
选择任意请求
↓
Request Headers 中找到 Cookie 行
↓
看到一长串 name=value; name2=value2; ...
```

**方法 B：使用 Application 标签（更直观）**

1. 点击开发者工具顶部的 **Application** 标签
2. 在左侧选择 **Cookies**
3. 点击 **https://www.ctrip.com**
4. 右侧会显示所有 Cookie（表格形式）

```
Application 标签
↓
左侧菜单找到 Cookies
↓
点击 www.ctrip.com
↓
右侧显示 Cookie 列表（name, value, domain 等）
```

#### 步骤 5：复制 Cookie 值

**方法 A：从 Network 标签复制（推荐）**

1. 找到 **Cookie** 那一行
2. 整行选中并复制（Ctrl+C 或 Cmd+C）

```
示例 Cookie 值：
bid=cpZzjq10lFI; _abtest_userid=9a8b7c6d5e4f3g2h1i; cticket=9E4CB5E6E8B9C7D8E9F0A1B2C3D4E5F6; __c=1705123456;...
```

**方法 B：从 Application 标签逐个复制**

1. 在 Cookie 列表中，逐个查看 name 和 value
2. 手动组合成字符串或 JSON 格式

```
表格格式：
| Name        | Value                      |
|-------------|---------------------------|
| bid         | cpZzjq10lFI              |
| _abtest_... | 9a8b7c6d5e4f3g2h1i       |
| cticket     | 9E4CB5E6E8B9C7D8E9F0A... |
```

### 🔗 方法 2：使用浏览器扩展（可选）

如果手动复制比较麻烦，可以安装 Cookie 导出扩展：

**推荐扩展：Cookie Editor**

1. 访问 Chrome 应用商店：https://chromewebstore.google.com/search/cookie%20editor
2. 找到 "Cookie Editor" 扩展
3. 点击 **添加至 Chrome**
4. 打开携程网站
5. 点击扩展图标 → **Export** → 复制 JSON 格式的 Cookie

---

## Cookie 格式说明

### 格式 1：字符串格式（Playwright 自动解析）

```python
# 完整 Cookie 字符串示例
COOKIES = "bid=cpZzjq10lFI; _abtest_userid=9a8b7c6d5e4f3g2h1i; cticket=9E4CB5E6E8B9C7D8E9F0A1B2C3D4E5F6; __c=1705123456; SESSION=xxx; ..."
```

**优点：**
- ✅ 格式简单，直接从浏览器复制
- ✅ 爬虫自动处理

**缺点：**
- ❌ 不够规范，可能丢失某些属性

### 格式 2：JSON 列表格式（推荐）

```python
# JSON 格式 Cookie 示例
COOKIES = '''[
  {"name": "bid", "value": "cpZzjq10lFI"},
  {"name": "_abtest_userid", "value": "9a8b7c6d5e4f3g2h1i"},
  {"name": "cticket", "value": "9E4CB5E6E8B9C7D8E9F0A1B2C3D4E5F6"},
  {"name": "__c", "value": "1705123456"},
  {"name": "SESSION", "value": "xxx"},
  {"name": "dbcl2", "value": "293236485:f1ioEyFSfRo"}
]'''
```

**优点：**
- ✅ 格式规范，易于管理
- ✅ 可以保留所有 Cookie 属性
- ✅ 与豆瓣爬虫格式一致

**缺点：**
- ❌ 需要手动格式化或使用扩展

### 格式 3：JavaScript 对象数组（编程方式）

如果你想用 Python 生成 JSON 格式的 Cookie：

```python
import json

# 从浏览器复制的字符串
cookie_string = "bid=cpZzjq10lFI; _abtest_userid=9a8b7c6d5e4f3g2h1i; SESSION=xxx"

# 转换为 JSON 格式
cookies_list = []
for pair in cookie_string.split('; '):
    if '=' in pair:
        name, value = pair.split('=', 1)
        cookies_list.append({"name": name, "value": value})

# 输出 JSON
cookies_json = json.dumps(cookies_list, ensure_ascii=False)
print(cookies_json)

# 输出示例：
# [{"name": "bid", "value": "cpZzjq10lFI"}, {"name": "_abtest_userid", "value": "9a8b7c6d5e4f3g2h1i"}, ...]
```

---

## 配置 Cookie

### 📝 步骤 1：编辑配置文件

打开文件：`/config/base_config.py`

找到这一行：

```python
COOKIES = '[{"name":"bid","value":"cpZzjq10lFI"},{"name":"dbcl2","value":"293236485:f1ioEyFSfRo"}]'
```

### 📝 步骤 2：替换为你的 Cookie

**方式 A：字符串格式**

```python
COOKIES = "bid=cpZzjq10lFI; _abtest_userid=9a8b7c6d5e4f3g2h1i; cticket=9E4CB5E6..."
```

**方式 B：JSON 格式（推荐）**

```python
COOKIES = '''[
  {"name": "bid", "value": "cpZzjq10lFI"},
  {"name": "_abtest_userid", "value": "9a8b7c6d5e4f3g2h1i"},
  {"name": "cticket", "value": "9E4CB5E6E8B9C7D8E9F0A1B2C3D4E5F6"},
  {"name": "SESSION", "value": "你的SESSION值"}
]'''
```

### 📝 步骤 3：保存配置文件

在编辑器中：
- **Windows/Linux**: Ctrl+S
- **macOS**: Cmd+S

---

## 验证 Cookie 有效性

### 方法 1：简单验证

```bash
# 启动爬虫，查看日志信息
cd /Users/kang/Desktop/MediaCrawler
python main.py
```

**成功标志：**
```
[CtripLogin.login_by_cookies] 开始 Cookie 登录...
[CtripLogin.login_by_cookies] 准备添加 X 个 Cookie
[CtripLogin.login_by_cookies] Cookie 已添加到浏览器
[CtripLogin.login_by_cookies] Cookie 登录成功，检测到有效 SESSION
[CtripCrawler.search] Found X reviews on page 1
```

**失败标志：**
```
[CtripCrawler.search] Page is blocked or requires verification
```

### 方法 2：手动验证脚本

创建文件 `test_cookie.py`：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import config

print("=" * 60)
print("携程 Cookie 配置验证")
print("=" * 60)

# 检查 Cookie 是否配置
if not config.COOKIES:
    print("❌ COOKIES 未配置")
    exit(1)

print(f"✓ COOKIES 已配置")

# 尝试解析 Cookie
try:
    cookies_list = eval(config.COOKIES)
    print(f"✓ Cookie 格式有效")
    print(f"✓ Cookie 数量: {len(cookies_list)}")
    
    # 显示前几个 Cookie
    for i, cookie in enumerate(cookies_list[:3]):
        if isinstance(cookie, dict):
            name = cookie.get("name", "N/A")
            value = cookie.get("value", "N/A")[:20] + "..." if len(str(cookie.get("value", ""))) > 20 else cookie.get("value", "N/A")
            print(f"  [{i+1}] {name} = {value}")
        else:
            print(f"  [警告] 第 {i+1} 个 Cookie 不是字典格式")
    
    if len(cookies_list) > 3:
        print(f"  ... 还有 {len(cookies_list) - 3} 个 Cookie")
        
except Exception as e:
    print(f"❌ Cookie 解析失败: {e}")
    exit(1)

# 检查关键 Cookie
cookies_dict = {}
if isinstance(cookies_list, list):
    for cookie in cookies_list:
        if isinstance(cookie, dict):
            cookies_dict[cookie.get("name")] = cookie.get("value")

print()
print("关键 Cookie 检查：")

critical_cookies = ["bid", "SESSION", "_abtest_userid", "dbcl2"]
for cookie_name in critical_cookies:
    if cookie_name in cookies_dict:
        value = cookies_dict[cookie_name][:10] + "..." if len(cookies_dict[cookie_name]) > 10 else cookies_dict[cookie_name]
        print(f"  ✓ {cookie_name}: {value}")
    else:
        print(f"  ⚠️ {cookie_name}: 未找到（可能不影响功能）")

print()
print("=" * 60)
print("✓ Cookie 配置验证完成！可以开始爬虫了")
print("=" * 60)
```

运行验证：

```bash
cd /Users/kang/Desktop/MediaCrawler
python test_cookie.py
```

**输出示例：**
```
============================================================
携程 Cookie 配置验证
============================================================
✓ COOKIES 已配置
✓ Cookie 格式有效
✓ Cookie 数量: 8
  [1] bid = cpZzjq10lFI
  [2] _abtest_userid = 9a8b7c6d5e4f3g2...
  [3] cticket = 9E4CB5E6E8B9C7D8...
  ... 还有 5 个 Cookie

关键 Cookie 检查：
  ✓ bid: cpZzjq10lFI
  ✓ SESSION: xxx...
  ✓ _abtest_userid: 9a8b7c6d...
  ⚠️ dbcl2: 未找到（可能不影响功能）

============================================================
✓ Cookie 配置验证完成！可以开始爬虫了
============================================================
```

### 方法 3：在线 Cookie 检查

使用 Python 直接测试：

```bash
python -c "
import config
import json

try:
    cookies = eval(config.COOKIES)
    if isinstance(cookies, list) and len(cookies) > 0:
        print('✅ Cookie 配置有效，共', len(cookies), '个')
    else:
        print('❌ Cookie 格式错误')
except Exception as e:
    print('❌ Cookie 解析失败:', e)
"
```

---

## Cookie 更新频率

### Cookie 何时过期

- **有效期**: 通常 7-30 天
- **自动过期**: 用户在网站上登出后
- **强制过期**: 清除浏览器 Cookie 或缓存

### 如何检查 Cookie 是否过期

运行爬虫时看到以下错误：

```
[CtripCrawler.search] Page is blocked or requires verification
```

这通常说明 Cookie 已过期，需要重新获取。

### 更新 Cookie

1. 重复上面的"获取步骤"
2. 获取新的 Cookie 值
3. 更新 `config/base_config.py`
4. 重新运行爬虫

---

## 常见问题

### Q1: 不登录可以获取 Cookie 吗？

**A**: 可以。未登录的情况下，浏览器仍然会设置一些默认 Cookie（如 `bid`）。但登录后的 Cookie 权限更多，能爬取更多内容。

**建议**: 登录后再获取 Cookie，效果更好。

### Q2: Cookie 中有密码或敏感信息吗？

**A**: Cookie 不包含密码。它们是服务器给浏览器的会话令牌，只表示"你已认证"，不包含密码。

**但要注意**:
- ⚠️ 不要将 Cookie 分享给他人
- ⚠️ 不要上传到公开的代码仓库
- ⚠️ 建议定期更新 Cookie

### Q3: 为什么 Cookie 复制后无法使用？

**A**: 可能的原因：

1. **格式错误**
   ```python
   # ❌ 错误：少了字符或格式混乱
   COOKIES = "bid=xxx; SESSION=yyy"
   
   # ✅ 正确：完整的字符串或 JSON
   COOKIES = "bid=xxx; SESSION=yyy; ..."
   ```

2. **Cookie 过期**
   ```
   解决：重新从浏览器获取最新 Cookie
   ```

3. **字符编码问题**
   ```python
   # 确保使用 UTF-8 编码
   # 在文件开头添加：
   # -*- coding: utf-8 -*-
   ```

4. **缺少必要字段**
   ```
   确保 Cookie 包含 bid、SESSION 等关键字段
   ```

### Q4: 多个 Cookie 值之间用什么分隔？

**A**: 取决于格式：

```python
# 字符串格式：分号 + 空格 分隔
COOKIES = "name1=value1; name2=value2; name3=value3"

# JSON 格式：用 JSON 数组和对象分隔
COOKIES = '''[
  {"name": "name1", "value": "value1"},
  {"name": "name2", "value": "value2"}
]'''
```

### Q5: 开发者工具中的 Cookie 很多，全部都需要吗？

**A**: 不需要。但最好全部复制，因为：

- ✅ 某些 Cookie 可能是爬虫成功的关键
- ✅ 部分 Cookie 用于分析和追踪
- ✅ 完整 Cookie 提高登录验证成功率

**如果实在太多，至少保留这些：**
- `bid` - 浏览器 ID
- `SESSION` - 会话令牌
- `_abtest_userid` - A/B 测试用户 ID
- `dbcl2` - 登录认证（如果已登录）

### Q6: Cookie 在什么时候会自动删除？

**A**: 以下情况会删除 Cookie：

1. 浏览器关闭后（临时 Cookie）
2. 清除浏览历史/Cookie 时
3. Cookie 过期时间到达
4. 手动从开发者工具删除
5. 用户在网站上点击"登出"

**建议**: 获取 Cookie 后立即配置到 `config.py`，避免关闭浏览器后 Cookie 丢失。

### Q7: 能否在多台机器上使用同一个 Cookie？

**A**: 技术上可以，但不推荐：

- ⚠️ Cookie 与浏览器的 User-Agent 关联
- ⚠️ 同时使用可能被服务器检测
- ⚠️ IP 地址变化可能导致 Cookie 失效

**建议**: 每台机器使用各自的 Cookie。

### Q8: 如何批量管理多个 Cookie？

**A**: 创建多个配置文件：

```
config/
├── base_config.py          # 默认配置
├── config_machine1.py      # 机器 1 的 Cookie
├── config_machine2.py      # 机器 2 的 Cookie
└── config_test.py          # 测试用 Cookie
```

运行时指定配置：

```bash
# 方式 1：修改 base_config.py 中的导入
python main.py

# 方式 2：编程方式动态选择
# 在 main.py 中添加：
# import sys
# if '--config' in sys.argv:
#     config_name = sys.argv[sys.argv.index('--config') + 1]
#     exec(f"from config import {config_name} as config")
```

---

## ✅ 快速检查清单

在开始爬虫前，确保：

- [ ] 已访问 https://www.ctrip.com
- [ ] 已登录携程账户（可选但推荐）
- [ ] 已打开开发者工具（F12 或 Cmd+Option+I）
- [ ] 已找到并复制 Cookie 值
- [ ] 已更新 `/config/base_config.py`
- [ ] Cookie 格式正确（字符串或 JSON）
- [ ] 运行了验证脚本 (`test_cookie.py`)
- [ ] 看到 "Cookie 登录成功" 的日志

完成以上步骤后，就可以开始爬虫了！

---

## 🚀 下一步

配置好 Cookie 后：

1. **运行爬虫**
   ```bash
   python main.py
   ```

2. **查看结果**
   ```bash
   ls -lh data/ctrip/
   ```

3. **如果遇到问题**
   - 查看 [故障排除指南](./ctrip_troubleshooting.md)
   - 更新 Cookie 重试
   - 启用代理重试

---

**有问题？** 参考 [完整使用指南](./ctrip_usage_guide.md) 或 [快速参考](./ctrip_quick_reference.md)

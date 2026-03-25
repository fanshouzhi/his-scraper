---
name: firecrawl
description: 本地 Firecrawl 网页爬取服务 + HIS 爬取方法论。使用场景：(1) 抓取网页内容转 Markdown，(2) 批量爬取整站，(3) 获取站点地图，(4) 爬取内网/私有 IP 页面，(5) 云HIS系统爬取。触发词：firecrawl、爬取网页、抓取页面、scrape、crawl、网页转markdown、HIS、医院。
---

# Firecrawl 本地服务 + HIS 爬取方法论

## 服务信息

- **地址**：`http://localhost:3002`
- **无需 API Key**（本地部署，认证已关闭）
- **支持内网**：已配置 `ALLOW_LOCAL_WROKS=true`，可访问私有 IP
- **管理面板**：`http://localhost:3002/admin/firecrawl-admin-2026/queues`

---

## 🚀 快速开始

### Shell 单次爬取

```bash
curl -s -X POST http://localhost:3002/v1/scrape \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com", "formats": ["markdown"], "onlyMainContent": true}'
```

### Python 封装（推荐）

```python
import requests
import json
from pathlib import Path

FIRECRAWL_API = "http://localhost:3002/v1/scrape"

def scrape(url, formats=None, only_main_content=True, wait_for=2000, timeout=60000, headers=None):
    payload = {
        "url": url,
        "formats": formats or ["markdown"],
        "onlyMainContent": only_main_content,
        "waitFor": wait_for,
        "timeout": timeout
    }
    if headers:
        payload["headers"] = headers
    
    resp = requests.post(FIRECRAWL_API, json=payload, timeout=timeout / 1000 + 10)
    return resp.json()
```

---

## 🎯 HIS 爬取核心方法论

### 问题分类与解决方案

| 问题类型 | 特征 | 解决方案 |
|----------|------|----------|
| **静态内容** | 表格、列表、文字 | Firecrawl 直接爬取 ✅ |
| **SPA应用** | JS渲染、菜单、iframe | Playwright 截图 |
| **交互弹窗** | 按钮点击、表单提交 | Playwright 操作 |
| **服务端报错** | 500/NullPointerException | 需要先建立会话 |

### 🔄 混合模式工作流

```
┌─────────────────────────────────────────────────────────┐
│  1. Playwright 登录 + 获取 Cookie                       │
│     ↓                                                  │
│  2. Firecrawl 获取静态数据（表格、列表）                 │
│     ↓                                                  │
│  3. Playwright 截图（页面视觉、弹窗状态）                │
│     ↓                                                  │
│  4. 验证结果 + 保存到 Notes                             │
└─────────────────────────────────────────────────────────┘
```

### 💡 云HIS 爬取经验

#### 1. Cookie 失效 → 自动登录脚本

```python
from playwright.sync_api import sync_playwright

HIS_URL = "http://172.16.8.20:8080/his"
USERNAME = "zsgly"
PASSWORD = "1"

def login_and_get_cookie():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto(f"{HIS_URL}/login.htm")
        page.wait_for_load_state("networkidle")
        
        page.fill("#key", USERNAME)
        page.fill("#passwordtext", PASSWORD)
        page.wait_for_timeout(300)
        page.click("#login_confirm")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        cookies = context.cookies()
        return cookies

def get_cookie_str(cookies):
    return "; ".join([f"{c['name']}={c['value']}" for c in cookies])
```

#### 2. SPA 页面 → 不要直接爬 URL

- 主页/菜单是 SPA，Firecrawl 只能获取登录页
- 需要 Playwright 截图或访问实际数据页

#### 3. URL 后缀规律

- 页面模块：`/home.json` 或 `/home.html`
- API 数据：`/home.json` 往往更有效
- 管理页面：优先尝试 `.json` 后缀

#### 4. 菜单点击 → 必须先访问主页建立会话

```python
# ❌ 错误：直接访问会报错
page.goto("http://xxx/others.htm?menuid=98")

# ✅ 正确：先登录 → 访问主页 → 再点击菜单
page.goto(f"{HIS_URL}/login.htm")  # 登录
page.fill("#key", USERNAME)
page.fill("#passwordtext", PASSWORD)
page.click("#login_confirm")
page.wait_for_timeout(2000)

page.goto(f"{HIS_URL}/platform.htm")  # 建立会话
page.wait_for_timeout(2000)
page.locator('li:has-text("预约挂号")').click()  # 点击菜单
page.wait_for_timeout(5000)  # 等待 SPA 加载
```

#### 5. 服务端报错 → 换一种方式

```python
# Firecrawl 报 404 或 NullPointerException
# 尝试：Playwright 直接访问该 URL（可能有会话就能访问）
```

---

## 📋 HIS 爬取标准流程

### 完整脚本

```python
#!/usr/bin/env python3
"""his_scraper.py - 云HIS自动爬取工具"""
import requests
import json
import os
from playwright.sync_api import sync_playwright
from datetime import datetime

HIS_URL = "http://172.16.8.20:8080/his"
FIRECRAWL = "http://localhost:3002/v1/scrape"
SAVE_DIR = "~/myWork/Notes/hisV3"

def login():
    """登录获取 Cookie"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto(f"{HIS_URL}/login.htm")
        page.wait_for_load_state("networkidle")
        page.fill("#key", "zsgly")
        page.fill("#passwordtext", "1")
        page.click("#login_confirm")
        page.wait_for_timeout(2000)
        
        cookies = context.cookies()
        with open(f"{SAVE_DIR}/cookie.json", "w") as f:
            json.dump(cookies, f)
        
        browser.close()
        return cookies

def firecrawl_scrape(url, cookies, name):
    """使用 Firecrawl 爬取"""
    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    
    payload = {
        "url": url,
        "formats": ["markdown", "html"],
        "waitFor": 8000,
        "headers": {"Cookie": cookie_str}
    }
    
    resp = requests.post(FIRECRAWL, json=payload, timeout=60)
    result = resp.json()
    
    if result.get("success"):
        md = result["data"].get("markdown", "")
        html = result["data"].get("html", "")
        
        with open(f"{SAVE_DIR}/{name}.md", "w", encoding="utf-8") as f:
            f.write(md)
        with open(f"{SAVE_DIR}/{name}.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        return True, len(md)
    else:
        return False, result.get("error")

def playwright_screenshot(url, cookies, name):
    """使用 Playwright 截图"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        for c in cookies:
            context.add_cookies([c])
        
        page.goto(url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        
        page.screenshot(path=f"{SAVE_DIR}/{name}.png", full_page=True)
        browser.close()
        return True

def scrape_module(module_name, url, cookies):
    """爬取单个模块"""
    print(f"\n📦 爬取: {module_name}")
    print(f"   URL: {url}")
    
    # 1. Firecrawl 获取数据
    success, result = firecrawl_scrape(url, cookies, f"md_{module_name}")
    if success:
        print(f"   ✅ Markdown: {result} chars")
    else:
        print(f"   ⚠️ Firecrawl: {result}")
    
    # 2. Playwright 截图
    success = playwright_screenshot(url, cookies, f"png_{module_name}")
    if success:
        print(f"   ✅ 截图完成")

def main():
    os.makedirs(os.path.expanduser(SAVE_DIR), exist_ok=True)
    
    # 1. 登录
    print("🔐 登录 HIS...")
    cookies = login()
    print("✅ 登录成功")
    
    # 2. 定义要爬取的模块
    modules = [
        ("班次维护", "http://172.16.8.20:8080/his/kyee/outp/shiftInfoManager/home.json"),
        ("排班模板", "http://172.16.8.20:8080/his/schedule_mode_gt.htm"),
        ("门诊挂号", "http://172.16.8.20:8080/his/kyee/outp/register/home.json"),
    ]
    
    # 3. 爬取每个模块
    for name, url in modules:
        scrape_module(name, url, cookies)
    
    print("\n🎉 完成！")

if __name__ == "__main__":
    main()
```

---

## 🔧 服务管理

### 启动/停止

```bash
cd ~/firecrawl && docker compose up -d      # 启动
cd ~/firecrawl && docker compose stop        # 停止
cd ~/firecrawl && docker compose restart     # 重启
```

### 健康检查

```bash
curl -s http://localhost:3002/health
docker ps --filter "name=firecrawl"
```

---

## ❌ 常见问题

### 1. Firecrawl 返回 404

- URL 可能不存在，尝试 `.html` → `.json`
- 检查是否需要先登录

### 2. Cookie 过期

- 执行 `login()` 函数重新获取

### 3. SPA 内容为空

- 使用 Playwright 截图替代
- 增加 `wait_for_timeout`

### 4. 服务端报错 (NullPointerException)

- 需要先建立会话：访问 `platform.htm`
- 然后再访问目标页面

---

## 📁 HIS 相关路径

### 预约挂号模块 (menuid=98)

| 子模块 | URL |
|--------|-----|
| 预约挂号主页 | `/his/kyee/outp/register/home.json` |
| 今日排班 | Tab 页面 |
| 个人挂号 | Tab 页面 |
| 全院挂号 | Tab 页面 |
| 患者预约记录 | Tab 页面 |

### 排班管理

| 模块 | URL |
|------|-----|
| 班次维护 | `/his/kyee/outp/shiftInfoManager/home.json` |
| 排班模板维护 | `/his/schedule_mode_gt.htm` |
| 排班管理 | `/his/schedule_gt.htm` |

### 登录信息

- URL: `http://172.16.8.20:8080/his`
- 账号: `zsgly`
- 密码: `1`

---

*更新于: 2026-03-25*

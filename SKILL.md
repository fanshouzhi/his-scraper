---
name: his-scraper
description: 云HIS内网系统爬取工具。用于爬取医院信息管理系统内网页面，支持需要登录认证的JavaScript单页应用，触发弹窗获取表单内容。触发词：HIS、爬取医院、门诊、挂号、排班。
---

# 云HIS内网系统爬取工具

自动化爬取云HIS（医院信息系统）内网管理页面。

## 核心方法论

### 🎯 问题解决流程

```
遇到问题 → 分类判断 → 选择工具 → 执行 → 验证
```

**三类问题及解决方案：**

| 问题类型 | 特征 | 解决方案 |
|----------|------|----------|
| **静态内容** | 表格、列表、文字 | Firecrawl 直接爬取 |
| **SPA应用** | JS渲染、菜单、iframe | Playwright 截图 |
| **交互弹窗** | 按钮点击、表单提交 | Playwright 操作 |

### 🔄 混合模式工作流

```
┌─────────────────────────────────────────────────────────┐
│  1. Firecrawl 获取静态数据                               │
│     ↓ 获取 markdown/html                                │
│  2. Playwright 处理交互                                 │
│     ↓ 截图、点击、弹窗                                  │
│  3. 验证结果                                           │
│     ↓ 保存到 Notes/                                    │
└─────────────────────────────────────────────────────────┘
```

**原则：**
- 静态内容用 Firecrawl（快速、节省资源）
- 交互内容用 Playwright（精准、可控）
- 两者结合才是最优解

### 💡 经验教训

1. **Cookie 失效 → 自动登录脚本**
   - 云HIS Cookie 有效期短
   - 当 Cookie 失效时，自动登录获取新 Cookie
   - 账号密码 + 无验证码 → 直接登录

2. **SPA 应用 → 不要直接爬 URL**
   - 主页/菜单是 SPA，Firecrawl 只能获取登录页
   - 需要 Playwright 截图或访问实际数据页

3. **URL 后缀规律**
   - 页面模块：`/home.json` 或 `/home.html`
   - API 数据：`/home.json`
   - 管理页面：`/home.json` 往往更有效

---

## 前置要求

```bash
# 1. Firecrawl 服务
cd ~/firecrawl && docker compose up -d

# 2. Playwright
pip3 install playwright
python3 -m playwright install chromium
```

---

## 快速开始

### 方法一：自动登录 + 爬取（推荐）

```python
#!/usr/bin/env python3
"""his_auto_scrape.py - 自动登录并爬取模块"""
import subprocess
import json
import os
from playwright.sync_api import sync_playwright

HIS_URL = "http://172.16.8.20:8080/his"
USERNAME = "zsgly"
PASSWORD = "1"
SAVE_DIR = "~/myWork/Notes/hisV3"

def login_and_get_cookie():
    """自动登录获取有效 Cookie"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # 访问登录页
        page.goto(f"{HIS_URL}/login.htm")
        page.wait_for_load_state("networkidle")
        
        # 填入账号密码
        page.fill("#key", USERNAME)
        page.fill("#passwordtext", PASSWORD)
        page.wait_for_timeout(500)
        
        # 点击登录
        page.click("#login_confirm")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # 获取新 Cookie
        cookies = context.cookies()
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        
        # 保存 Cookie
        os.makedirs(SAVE_DIR, exist_ok=True)
        with open(f"{SAVE_DIR}/cookie.json", "w") as f:
            json.dump(cookies, f)
        
        browser.close()
        return cookie_str

def firecrawl_scrape(url, cookie, filename):
    """使用 Firecrawl 爬取页面"""
    data = json.dumps({
        "url": url,
        "formats": ["markdown", "html"],
        "waitFor": 8000,
        "headers": {"Cookie": cookie}
    }).encode()
    
    req = subprocess.Popen(
        ['curl', '-s', '-X', 'POST', 'http://localhost:3002/v1/scrape',
         '-H', 'Content-Type: application/json',
         '-d', '@-'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, _ = req.communicate(input=data)
    result = json.loads(stdout)
    
    if result.get("success"):
        save_dir = os.path.expanduser(SAVE_DIR)
        # 保存 markdown
        md = result["data"].get("markdown", "")
        with open(f"{save_dir}/{filename}.md", "w", encoding="utf-8") as f:
            f.write(md)
        # 保存 html
        html = result["data"].get("html", "")
        with open(f"{save_dir}/{filename}.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ {filename}: {len(md)} chars")
        return True
    else:
        print(f"❌ {filename}: {result.get('error', 'Unknown error')}")
        return False

def playwright_screenshot(url, cookie_file, filename):
    """使用 Playwright 截图"""
    with open(os.path.expanduser(cookie_file)) as f:
        cookies = json.load(f)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        for c in cookies:
            context.add_cookies([c])
        
        page.goto(url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        save_path = os.path.expanduser(f"{SAVE_DIR}/{filename}.png")
        page.screenshot(path=save_path, full_page=True)
        print(f"✅ 截图: {save_path}")
        
        browser.close()

# 使用示例
if __name__ == "__main__":
    print("🚀 开始 HIS 爬取...")
    
    # 1. 登录获取 Cookie
    cookie = login_and_get_cookie()
    print(f"获取到 Cookie: {cookie[:50]}...")
    
    # 2. Firecrawl 爬取静态页面
    modules = [
        (f"{HIS_URL}/kyee/outp/shiftInfoManager/home.json", "03_bcwh"),
    ]
    
    for url, name in modules:
        firecrawl_scrape(url, cookie, name)
    
    # 3. Playwright 截图
    playwright_screenshot(
        f"{HIS_URL}/kyee/outp/shiftInfoManager/home.json",
        f"{SAVE_DIR}/cookie.json",
        "07_bcwh"
    )
    
    print("🎉 完成！")
```

### 方法二：直接使用已有 Cookie

```bash
# 1. Firecrawl 获取静态内容
curl -s -X POST http://localhost:3002/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://172.16.8.20:8080/his/kyee/outp/shiftInfoManager/home.json",
    "formats": ["markdown", "html"],
    "waitFor": 8000,
    "headers": {"Cookie": "SESSION=xxx; job_no=zsgly; vcode=xxx"}
  }'
```

### 方法三：Playwright 交互截图

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    # 设置 Cookie
    context.add_cookies([
        {"name": "SESSION", "value": "xxx", "domain": "172.16.8.20", "path": "/"},
        {"name": "job_no", "value": "zsgly", "domain": "172.16.8.20", "path": "/"},
    ])
    
    # 访问页面
    page.goto("http://172.16.8.20:8080/his/kyee/outp/shiftInfoManager/home.json")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)
    
    # 截图
    page.screenshot(path="screenshot.png", full_page=True)
    
    # 点击新增按钮
    page.click("button:has-text('新增')")
    page.wait_for_timeout(3000)
    page.screenshot(path="modal.png", full_page=True)
    
    browser.close()
```

---

## Cookie 管理

### 当前可用 Cookie 格式

```
SESSION=xxx; job_no=zsgly; vcode=xxx
```

### 自动登录获取新 Cookie

当 Cookie 失效时，使用上面的 `login_and_get_cookie()` 函数自动获取。

### 手动获取步骤

1. 登录 HIS 系统
2. F12 → Application → Cookies → 172.16.8.20
3. 复制 SESSION 值

---

## 已测试模块

| 模块名称 | URL | Firecrawl | Playwright | 状态 |
|----------|-----|-----------|------------|------|
| 班次维护 | `/his/kyee/outp/shiftInfoManager/home.json` | ✅ | ✅ | ✅ 已测试 |
| 分时时段维护 | `/his/kyee/outp/clcTimeInfoManager/home.json` | ✅ | ✅ | ✅ 已测试 |
| 诊室信息维护 | `/his/kyee/outp/clcRoomInfoManager/home.json` | ✅ | ✅ | ✅ 已测试 |
| 排班模板维护 | `/his/schedule_mode_gt.htm` | ✅ | ✅ | ✅ 已测试 |
| 排班管理 | `/his/schedule_gt.htm` | ✅ | ✅ | ⏳ 待测试 |
| 门诊收费日报 | `/his/kyee/gt/report/clc/mzInvoiceShow.htm` | ✅ | ✅ | ⏳ 待测试 |
| 预约挂号主页 | `/his/kyee/outp/reg/appointmentreg/home.html` | ⚠️ 404 | ✅ | ✅ 已测试 |

---

## 常见问题排查

### Q: Firecrawl 返回 404？
**A:** URL 可能不存在，尝试：
- 将 `.html` 改为 `.json`
- 检查是否需要先登录
- 使用 Playwright 截图验证页面存在

### Q: Cookie 过期？
**A:** 执行自动登录脚本获取新 Cookie

### Q: Playwright 点击超时？
**A:** 
- 先按 `Escape` 关闭弹窗
- 使用 `page.locator("selector").first.click()` 
- 增加 `wait_for_timeout` 时间

### Q: SPA 应用无法爬取内容？
**A:** 这是正常的，SPA 需要 Playwright：
```python
# 截图保存
page.screenshot(path="screenshot.png", full_page=True)
# 获取 HTML（可能只是框架）
content = page.content()
```

### Q: 页面加载慢？
**A:** 增加等待时间：
```python
page.wait_for_load_state("networkidle")
page.wait_for_timeout(5000)  # 额外等待
```

---

## 目录结构

```
~/myWork/Notes/hisV3/
├── cookie.json           # 当前 Cookie
├── 01_main_page.md/html  # 主页面
├── 04_platform.png       # 主页面截图
├── 03_bcwh.md/html       # 班次维护数据
├── 07_bcwh.png           # 班次维护截图
└── ...
```

---

## 最佳实践

1. **每次爬取前检查 Cookie 有效性**
   - 访问主页验证是否需要重新登录

2. **混合使用 Firecrawl 和 Playwright**
   - 表格数据用 Firecrawl（结构化）
   - 截图用 Playwright（视觉验证）

3. **保存完整上下文**
   - Cookie + 截图 + Markdown 三件套

4. **记录失败案例**
   - 保存失败的 URL 和错误信息
   - 方便后续排查

---
更新于: 2026-03-25

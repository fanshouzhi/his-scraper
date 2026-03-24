---
name: his-scraper
description: 云HIS内网系统爬取工具。用于爬取医院信息管理系统内网页面，支持需要登录认证的JavaScript单页应用，触发弹窗获取表单内容。触发词：HIS、爬取医院、门诊、挂号、排班。
---

# 云HIS内网系统爬取工具

自动化爬取云HIS（医院信息系统）内网管理页面。

## 爬取规则（重要）

**每次爬取必须使用混合模式：**

1. **第一步：Firecrawl** - 获取页面基本结构
   - 快速获取列表数据、表格内容
   - 保存 Markdown/HTML 格式
2. **第二步：Playwright** - 处理交互操作
   - 按钮点击、弹窗内容
   - 截图保存关键页面状态

**禁止直接使用 Playwright 获取静态内容！**

## 前置要求

1. **Firecrawl 服务**：`cd ~/firecrawl && docker compose up -d`
2. **Playwright**：`pip3 install playwright && python3 -m playwright install chromium`
3. **Cookie**：用户登录后从浏览器获取

## 快速开始

### 步骤一：Firecrawl 获取静态内容

```bash
curl -s -X POST http://localhost:3002/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://172.16.8.20:8080/his/模块URL",
    "formats": ["markdown", "html"],
    "waitFor": 5000,
    "headers": {"Cookie": "SESSION=xxx; job_no=zsgly; JSESSIONID=xxx"}
  }'
```

### 步骤二：Playwright 处理交互

```python
from playwright.sync_api import sync_playwright

cookie = {"name": "SESSION", "value": "xxx", "domain": "172.16.8.20", "path": "/his/"}
job_no = {"name": "job_no", "value": "zsgly", "domain": "172.16.8.20", "path": "/his/"}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    context.add_cookies([cookie, job_no])
    
    page.goto("http://172.16.8.20:8080/his/模块URL")
    page.wait_for_load_state("networkidle")
    
    # 截图
    page.screenshot(path="screenshot.png", full_page=True)
    
    # 点击按钮
    page.click("button:has-text('新增')")
    page.wait_for_timeout(3000)
    page.screenshot(path="modal.png", full_page=True)
    
    # 关闭弹窗
    page.keyboard.press("Escape")
    
    browser.close()
```

## Cookie 获取方式

1. 登录 HIS 系统
2. 打开浏览器开发者工具 (F12)
3. Application → Cookies → 点击域名
4. 复制 SESSION 值

**注意**：Cookie 有效期较短，每次会话需要重新获取。

## 已测试模块

| 模块名称 | URL | 状态 |
|----------|-----|------|
| 班次维护 | /his/kyee/outp/shiftInfoManager/home.json | ✅ 已测试 |
| 分时时段维护 | /his/kyee/outp/clcTimeInfoManager/home.json | ✅ 已测试 |
| 诊室信息维护 | /his/kyee/outp/clcRoomInfoManager/home.json | ✅ 已测试 |
| 排班模板维护 | /his/schedule_mode_gt.htm | ✅ 已测试 |
| 排班管理 | /his/schedule_gt.htm | ⏳ 待测试 |
| 门诊收费日报 | /his/kyee/gt/report/clc/mzInvoiceShow.htm | ⏳ 待测试 |

## 常见问题

**Q: Cookie 过期了？**
A: 每次会话需要重新获取新的 Cookie

**Q: 点击按钮超时？**
A: 先按 Escape 关闭弹窗再操作

**Q: 找不到元素？**
A: 使用 `page.locator("selector").first.click()` 或 JavaScript 点击

## 保存位置

- **笔记目录**: `~/myWork/Notes/his/`
- **命名规范**: `his_{模块名}_{类型}.md/html/png`

---
更新于: 2026-03-24

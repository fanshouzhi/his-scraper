---
name: his-scraper
description: 云HIS内网系统爬取工具。用于爬取医院信息管理系统内网页面，支持需要登录认证的JavaScript单页应用，触发弹窗获取表单内容。触发词：HIS、爬取医院、门诊、挂号、排班。
---

# 云HIS内网系统爬取

自动化爬取云HIS（医院信息系统）内网管理页面。

## 前置要求

1. **Firecrawl 服务**：`cd ~/firecrawl && docker compose up -d`
2. **Playwright**：`pip3 install playwright && python3 -m playwright install chromium`
3. **Cookie**：用户登录后从浏览器获取

## 快速开始

### 方式一：Firecrawl（静态页面）

适合抓取不需要交互的页面内容。

```bash
# 设置 Cookie
export HIS_COOKIE="SESSION=xxx; job_no=zsgly; JSESSIONID=xxx"

# 抓取页面
curl -s -X POST http://localhost:3002/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://172.16.8.20:8080/his/模块URL",
    "formats": ["markdown", "html"],
    "waitFor": 5000,
    "headers": {"Cookie": "SESSION=xxx; job_no=zsgly; JSESSIONID=xxx"}
  }'
```

### 方式二：Playwright（交互式页面）

适合需要点击按钮、触发弹窗等交互操作的场景。

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
4. 复制 SESSION 和 JSESSIONID 值

**注意**：Cookie 有效期较短，每次会话需要重新获取。

## 支持模块

| 模块 | URL |
|------|-----|
| 班次维护 | /his/kyee/outp/shiftInfoManager/home.json |
| 分时时段维护 | /his/kyee/outp/timeSlotConfig/home.json |
| 诊室信息维护 | /his/kyee/outp/roomInfo/home.json |
| 排班管理 | /his/schedule_gt.htm |
| 门诊收费日报 | /his/kyee/gt/report/clc/mzInvoiceShow.htm |

## 爬取方法论

### 1. 静态内容抓取 (Firecrawl)

适用于：
- 列表页面（表格数据）
- 搜索结果
- 页面基本结构

**优点**：快速、无需维护浏览器
**缺点**：无法处理登录验证和复杂交互

### 2. 交互式抓取 (Playwright)

适用于：
- 按钮点击
- 弹窗内容
- 表格行选中
- 表单提交

**优点**：可模拟真实用户操作
**缺点**：需要处理弹窗覆盖问题

### 3. 混合模式

推荐工作流：
1. 用 Firecrawl 快速获取页面基本结构
2. 用 Playwright 处理交互操作（点击、弹窗）
3. 截图保存关键页面状态

### 4. 常见问题

**Q: Cookie 过期了？**
A: 每次会话需要重新获取新的 Cookie

**Q: 点击按钮超时？**
A: 检查是否有弹窗覆盖 (`.dhxwins_mcover`)，先关闭弹窗再操作

**Q: 找不到元素？**
A: 使用 `page.locator("selector").first.click()` 替代直接 click

## 保存位置

- **笔记目录**: `~/myWork/Notes/his/`
- **命名规范**: `his_{模块名}_{类型}.md/html/png`

## 脚本说明

- [scripts/his_scrape.py](scripts/his_scrape.py) - 主页面抓取
- [scripts/his_modal.py](scripts/his_modal.py) - 弹窗触发抓取

---
更新于: 2026-03-24

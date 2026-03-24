# 云HIS内网系统爬取工具

自动化爬取云HIS（医院信息系统）内网管理页面。

## 功能特点

- 支持需要登录认证的内网页面抓取
- 支持按钮点击、弹窗交互等操作
- 支持页面截图保存
- 支持 Markdown/HTML 格式输出

## 前置要求

1. **Firecrawl 服务**：
   ```bash
   cd ~/firecrawl && docker compose up -d
   ```

2. **Playwright**：
   ```bash
   pip3 install playwright
   python3 -m playwright install chromium
   ```

3. **Cookie**：用户登录后从浏览器获取

## 快速开始

### 方式一：Firecrawl（静态页面）

适合抓取不需要交互的页面内容。

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

### 方式二：Playwright（交互式页面）

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

## 已测试模块

| 模块名称 | URL |
|----------|-----|
| 班次维护 | /his/kyee/outp/shiftInfoManager/home.json |
| 分时时段维护 | /his/kyee/outp/clcTimeInfoManager/home.json |

## 爬取方法论

### 1. 静态内容抓取 (Firecrawl)
- 适用于：列表页面、搜索结果、页面基本结构
- 优点：快速、无需维护浏览器
- 缺点：无法处理登录验证和复杂交互

### 2. 交互式抓取 (Playwright)
- 适用于：按钮点击、弹窗内容、表格行选中、表单提交
- 优点：可模拟真实用户操作
- 缺点：需要处理弹窗覆盖问题

### 3. 常见问题

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

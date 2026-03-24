# HIS Scraper

Automated scraping tool for Cloud HIS (Hospital Information System) intranet pages.

## Scraping Rules (Important)

**Every scraping must use hybrid mode:**

1. **Step 1: Firecrawl** - Get page basic structure
   - Quick fetch of list data, table content
   - Save as Markdown/HTML format
2. **Step 2: Playwright** - Handle interactive operations
   - Button clicks, modal content
   - Screenshot key page states

**DO NOT use Playwright directly for static content!**

## Features

- Supports authenticated intranet page scraping
- Supports button clicks, modal interactions
- Supports page screenshot capture
- Supports Markdown/HTML output

## Prerequisites

1. **Firecrawl Service**:
   ```bash
   cd ~/firecrawl && docker compose up -d
   ```

2. **Playwright**:
   ```bash
   pip3 install playwright
   python3 -m playwright install chromium
   ```

3. **Cookie**: Get from browser after login

## Quick Start

### Step 1: Firecrawl for Static Content

```bash
curl -s -X POST http://localhost:3002/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://172.16.8.20:8080/his/moduleURL",
    "formats": ["markdown", "html"],
    "waitFor": 5000,
    "headers": {"Cookie": "SESSION=xxx; job_no=zsgly; JSESSIONID=xxx"}
  }'
```

### Step 2: Playwright for Interaction

```python
from playwright.sync_api import sync_playwright

cookie = {"name": "SESSION", "value": "xxx", "domain": "172.16.8.20", "path": "/his/"}
job_no = {"name": "job_no", "value": "zsgly", "domain": "172.16.8.20", "path": "/his/"}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    context.add_cookies([cookie, job_no])
    
    page.goto("http://172.16.8.20:8080/his/moduleURL")
    page.wait_for_load_state("networkidle")
    
    # Screenshot
    page.screenshot(path="screenshot.png", full_page=True)
    
    # Click button
    page.click("button:has-text('Add')")
    page.wait_for_timeout(3000)
    page.screenshot(path="modal.png", full_page=True)
    
    # Close modal
    page.keyboard.press("Escape")
    
    browser.close()
```

## How to Get Cookie

1. Login to HIS system
2. Open browser DevTools (F12)
3. Application → Cookies → click domain
4. Copy SESSION value

**Note**: Cookie expires frequently, need to get new one each session.

## Tested Modules

| Module Name | URL |
|-------------|-----|
| 班次维护 (Shift Info) | /his/kyee/outp/shiftInfoManager/home.json |
| 分时时段维护 (Time Slots) | /his/kyee/outp/clcTimeInfoManager/home.json |
| 诊室信息维护 (Room Info) | /his/kyee/outp/clcRoomInfoManager/home.json |
| 排班模板维护 (Schedule Template) | /his/schedule_mode_gt.htm |

## Common Issues

**Q: Cookie expired?**
A: Get new Cookie for each session

**Q: Click timeout?**
A: Press Escape to close modal first

**Q: Element not found?**
A: Use `page.locator("selector").first.click()` or JavaScript click

## Save Location

- **Notes**: `~/myWork/Notes/his/`
- **Naming**: `his_{module}_{type}.md/html/png`

---
Updated: 2026-03-24

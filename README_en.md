# HIS Scraper - Cloud HIS Intranet Crawling Tool

A complete automation solution for crawling Cloud HIS (Hospital Information System) intranet management pages.

## Features

- ✅ Supports intranet private IP page crawling
- ✅ Supports systems requiring login authentication
- ✅ Supports triggering popups to capture form content
- ✅ Supports automatic CAPTCHA recognition
- ✅ Complete appointment registration module crawling workflow

## Requirements

- Python 3.9+
- Docker (for running Firecrawl)
- Playwright

## Quick Start

### 1. Install Dependencies

```bash
# Install Python packages
pip3 install playwright requests pillow pytesseract

# Install Playwright browsers
python3 -m playwright install chromium

# Start Firecrawl service
cd ~/firecrawl && docker compose up -d
```

### 2. Get Cookie

Recommended: Ask user to log in through browser and provide the Cookie.

### 3. Crawl Pages

```python
import subprocess
import json

cookie = "SESSION=xxx; job_no=zsgly; JSESSIONID=xxx"
url = "http://172.16.8.20:8080/his/kyee/outp/shiftInfoManager/home.json"

result = subprocess.run([
    'curl', '-s', '-X', 'POST', 'http://localhost:3002/v1/scrape',
    '-H', 'Content-Type: application/json',
    '-d', json.dumps({
        "url": url,
        "formats": ["markdown", "html"],
        "headers": {"Cookie": cookie}
    })
], capture_output=True, text=True)

data = json.loads(result.stdout)
print(data['data']['markdown'])
```

## Module URLs

| Module | URL |
|--------|-----|
| Shift Maintenance | /his/kyee/outp/shiftInfoManager/home.json |
| Time Slot Config | /his/kyee/outp/clcTimeInfoManager/home.json |
| Room Info | /his/kyee/outp/clcRoomInfoManager/home.json |
| Schedule Template | /his/schedule_mode_gt.htm |
| Schedule Management | /his/schedule_gt.htm |
| Daily Report | /his/kyee/gt/report/clc/mzInvoiceShow.htm |
| Invoice Request | /his/maintenance/chg_manage/basInvoice.htm |

## Documentation

- [Chinese Guide](./README_cn.md)

## Tech Stack

- **Firecrawl** - Web content scraping (intranet support)
- **Playwright** - Browser automation
- **Python** - Core scripting

## License

MIT

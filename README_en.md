# HIS Scraper - Cloud HIS Intranet Scraping Tool

Automated scraping tool for Cloud HIS (Hospital Information System) intranet pages.

## Features

- 🔐 **Auto Login** - No manual Cookie needed, supports automatic login
- 🌐 **Hybrid Mode** - Firecrawl + Playwright combination for speed and functionality
- 📸 **Screenshot** - Save key page screenshots
- 📊 **Data Export** - Markdown + HTML dual format output
- 🛠️ **Script Tools** - One-click scraping for specified modules

## Quick Start

### Install Dependencies

```bash
# Install Playwright
pip3 install playwright
python3 -m playwright install chromium

# Start Firecrawl service
cd ~/firecrawl && docker compose up -d
```

### Usage

```bash
# List available modules
python3 scrape_his.py --list

# Scrape single module
python3 scrape_his.py bcwh        # Shift Info Manager
python3 scrape_his.py fssd        # Time Slot Config
python3 scrape_his.py zsxx        # Room Info Manager

# Custom URL
python3 scrape_his.py --url '/his/kyee/outp/shiftInfoManager/home.json'

# Scrape all modules
python3 scrape_his.py --all
```

## Supported Modules

| Module | Path | Description |
|--------|------|-------------|
| Shift Info Manager | `/his/kyee/outp/shiftInfoManager/home.json` | Medical staff scheduling |
| Time Slot Config | `/his/kyee/outp/clcTimeInfoManager/home.json` | Time slot configuration |
| Room Info Manager | `/his/kyee/outp/clcRoomInfoManager/home.json` | Room management |
| Schedule Template | `/his/schedule_mode_gt.htm` | Schedule templates |
| Schedule Manager | `/his/schedule_gt.htm` | Schedule management |
| Appointment Main | `/his/kyee/outp/reg/appointmentreg/home.html` | Appointment registration |

## Methodology

### Hybrid Scraping Mode

```
┌─────────────────────────────────────────────────────────┐
│  1. Firecrawl - Get static data                       │
│     - Table content, list data                         │
│     - Fast speed, low resource usage                   │
│                                                         │
│  2. Playwright - Handle interactions                  │
│     - Button clicks, modal content                     │
│     - Screenshots, SPA applications                   │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Firecrawl** - Web scraping service
- **Playwright** - Browser automation
- **Python 3** - Scripting language

## License

MIT

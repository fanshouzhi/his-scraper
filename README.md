# HIS Scraper - 云HIS内网系统爬取工具

自动化爬取云HIS（医院信息系统）内网管理页面。

## 功能特点

- 🔐 **自动登录** - 无需手动获取 Cookie，支持自动登录
- 🌐 **混合模式** - Firecrawl + Playwright 组合，兼顾速度与功能
- 📸 **截图保存** - 关键页面截图保存
- 📊 **数据导出** - Markdown + HTML 双格式输出
- 🛠️ **脚本工具** - 一键爬取指定模块

## 快速开始

### 安装依赖

```bash
# 安装 Playwright
pip3 install playwright
python3 -m playwright install chromium

# 启动 Firecrawl 服务
cd ~/firecrawl && docker compose up -d
```

### 使用方法

```bash
# 进入脚本目录
cd ~/github/his-scraper/scripts

# 列出所有可用模块
python3 scrape_his.py --list

# 爬取单个模块
python3 scrape_his.py bcwh        # 班次维护
python3 scrape_his.py fssd        # 分时时段维护
python3 scrape_his.py zsxx        # 诊室信息维护
python3 scrape_his.py pbmb        # 排班模板维护

# 自定义 URL
python3 scrape_his.py --url '/his/kyee/outp/shiftInfoManager/home.json'

# 爬取所有模块
python3 scrape_his.py --all
```

## 已支持模块

| 模块 | 路径 | 说明 |
|------|------|------|
| 班次维护 | `/his/kyee/outp/shiftInfoManager/home.json` | 医护人员排班 |
| 分时时段维护 | `/his/kyee/outp/clcTimeInfoManager/home.json` | 时段配置 |
| 诊室信息维护 | `/his/kyee/outp/clcRoomInfoManager/home.json` | 诊室管理 |
| 排班模板维护 | `/his/schedule_mode_gt.htm` | 排班模板 |
| 排班管理 | `/his/schedule_gt.htm` | 排班管理 |
| 预约挂号主页 | `/his/kyee/outp/reg/appointmentreg/home.html` | 预约挂号 |

## 方法论

### 混合爬取模式

```
┌─────────────────────────────────────────────────────────┐
│  1. Firecrawl - 获取静态数据                            │
│     - 表格内容、列表数据                                 │
│     - 速度快、节省资源                                   │
│                                                         │
│  2. Playwright - 处理交互                               │
│     - 按钮点击、弹窗内容                                 │
│     - 截图保存、SPA 应用                                │
└─────────────────────────────────────────────────────────┘
```

### 问题排查

| 问题 | 解决方案 |
|------|----------|
| Cookie 失效 | 运行自动登录脚本获取新 Cookie |
| Firecrawl 404 | 尝试将 `.html` 改为 `.json` |
| Playwright 超时 | 增加 `wait_for_timeout` 时间 |
| SPA 内容为空 | 使用 Playwright 截图替代 |

## 目录结构

```
hisV3/
├── cookie.json           # 当前 Cookie
├── platform.png         # 主页截图
├── md_bcwh.md/html      # 班次维护数据
├── png_bcwh.png         # 班次维护截图
└── ...
```

## 技术栈

- **Firecrawl** - 网页爬取服务
- **Playwright** - 浏览器自动化
- **Python 3** - 脚本语言

## License

MIT

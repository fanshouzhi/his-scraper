# 云HIS内网系统爬取工具

本项目提供了一套完整的自动化方案，用于爬取云HIS（医院信息系统）内网管理页面的内容。

## 特性

- ✅ 支持内网私有IP页面抓取
- ✅ 支持需要登录认证的系统
- ✅ 支持触发弹窗获取表单内容
- ✅ 支持验证码自动识别
- ✅ 完整的预约挂号模块爬取流程

## 环境要求

- Python 3.9+
- Docker (用于运行Firecrawl)
- Playwright

## 快速开始

### 1. 安装依赖

```bash
# 安装Python包
pip3 install playwright requests pillow pytesseract

# 安装Playwright浏览器
python3 -m playwright install chromium

# 启动Firecrawl服务
cd ~/firecrawl && docker compose up -d
```

### 2. 获取Cookie

推荐方式：让用户在浏览器中登录后提供Cookie。

### 3. 抓取页面

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

## 模块列表

| 模块 | URL |
|------|-----|
| 班次维护 | /his/kyee/outp/shiftInfoManager/home.json |
| 分时时段维护 | /his/kyee/outp/clcTimeInfoManager/home.json |
| 诊室信息维护 | /his/kyee/outp/clcRoomInfoManager/home.json |
| 排班模板维护 | /his/schedule_mode_gt.htm |
| 排班管理 | /his/schedule_gt.htm |
| 门诊收费日报 | /his/kyee/gt/report/clc/mzInvoiceShow.htm |
| 发票申领 | /his/maintenance/chg_manage/basInvoice.htm |

## 详细文档

- [完整使用指南](./docs/guide.md)

## 技术栈

- **Firecrawl** - 网页内容抓取（支持内网）
- **Playwright** - 浏览器自动化
- **Python** - 核心脚本

## License

MIT

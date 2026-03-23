# 云HIS内网系统爬取Skill

## 功能描述

自动化爬取云HIS（医院信息系统）内网管理页面的完整工作流。

## 适用场景

- 爬取内网医院管理系统页面
- 需要登录认证的JavaScript单页应用
- 需要触发弹窗获取表单字段

## 前置要求

### 1. 环境依赖
```bash
# 安装 Playwright（用于弹窗触发）
pip3 install playwright

# 启动 Firecrawl 服务
cd ~/firecrawl && docker compose up -d
```

### 2. 登录凭证
- 系统URL: `http://172.16.8.20:8080/his`
- 账号: `zsgly`
- 密码: `1`
- 科室代码: `159`

## 使用方法

### 方式一：获取用户Cookie（推荐）

1. 用户在浏览器中登录系统
2. 用户提供浏览器中的Cookie
3. 使用Firecrawl抓取页面

```python
import subprocess
import json

cookie = "SESSION=xxx; job_no=zsgly; JSESSIONID=xxx"
url = "http://172.16.8.20:8080/his/模块URL"

result = subprocess.run([
    'curl', '-s', '-X', 'POST', 'http://localhost:3002/v1/scrape',
    '-H', 'Content-Type: application/json',
    '-d', json.dumps({
        "url": url,
        "formats": ["markdown", "html"],
        "onlyMainContent": True,
        "waitFor": 5000,
        "headers": {"Cookie": cookie}
    })
], capture_output=True, text=True)

data = json.loads(result.stdout)
markdown = data['data']['markdown']
```

### 方式二：自动登录（需验证码OCR）

```python
import requests
import base64
import time
from PIL import Image
import pytesseract

session = requests.Session()

# 1. 获取初始session
session.get("http://172.16.8.20:8080/his")

# 2. 识别验证码
vcode_resp = session.get("http://172.16.8.20:8080/his/vcode.htm")
with open('/tmp/vcode.png', 'wb') as f:
    f.write(vcode_resp.content)

img = Image.open('/tmp/vcode.png')
vcode = pytesseract.image_to_string(img, config='--psm 7').strip()
vcode = ''.join(c for c in vcode if c.isdigit())

# 3. 登录（密码需Base64编码）
password = base64.b64encode("1".encode('utf-8')).decode('utf-8')
params = {
    "key": "zsgly",
    "password": password,
    "vcode": vcode,
    "dept": "159",
    "time": str(int(time.time() * 1000))
}

resp = session.get("http://172.16.8.20:8080/his/checkUser.htm", params=params)
if "success" in resp.text:
    # 登录成功，使用session cookies
    cookie = "; ".join([f"{k}={v}" for k, v in session.cookies.items()])
```

### 触发弹窗抓取

使用Playwright触发按钮并获取弹窗内容：

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    # 设置Cookie
    context.add_cookies([
        {"name": "SESSION", "value": "xxx", "domain": "172.16.8.20", "path": "/his/"},
        {"name": "job_no", "value": "zsgly", "domain": "172.16.8.20", "path": "/his/"},
        {"name": "JSESSIONID", "value": "xxx", "domain": "172.16.8.20", "path": "/his/"},
    ])
    
    # 访问页面
    page.goto("http://172.16.8.20:8080/his/模块URL")
    page.wait_for_load_state("networkidle")
    
    # 点击按钮触发弹窗
    page.locator('button:has-text("新增")').click()
    page.wait_for_timeout(5000)
    
    # 获取弹窗iframe内容
    iframe = page.locator('.dhx_cell_cont_wins iframe').first
    iframe_src = iframe.get_attribute('src')
```

### Firecrawl抓取弹窗

从弹窗URL提取实际内容：

```python
# showAddView.json -> 新增弹窗
# showUpdateView.json -> 修改弹窗
modal_url = f"http://172.16.8.20:8080{iframe_src}"
```

## 预约挂号模块URL映射

| 菜单ID | 模块名称 | URL |
|--------|----------|-----|
| 9802 | 班次维护 | /his/kyee/outp/shiftInfoManager/home.json |
| 9803 | 分时时段维护 | /his/kyee/outp/clcTimeInfoManager/home.json |
| 9804 | 诊室信息维护 | /his/kyee/outp/clcRoomInfoManager/home.json |
| 9805 | 排班模板维护 | /his/schedule_mode_gt.htm |
| 9806 | 排班管理 | /his/schedule_gt.htm |
| 9807 | 门诊收费日报 | /his/kyee/gt/report/clc/mzInvoiceShow.htm |
| 9808 | 发票申领 | /his/maintenance/chg_manage/basInvoice.htm |

## 保存路径

- 笔记目录: `~/myWork/Notes/his/`
- 命名规范: `his_{模块名}_{类型}.md/html`

## 注意事项

1. 验证码识别OCR可能需要多次尝试
2. 弹窗内容通过iframe加载，需分别抓取
3. 内网系统需要先建立VPN连接
4. Cookie有效期有限，建议每次使用时让用户提供

## 技术栈

- Firecrawl: 网页内容抓取（支持内网）
- Playwright: 浏览器自动化
- Python requests: HTTP请求
- pytesseract: 验证码OCR识别

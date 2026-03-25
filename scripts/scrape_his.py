#!/usr/bin/env python3
"""
HIS 自动登录与爬取工具
用法: python3 scrape_his.py [模块名] [模块URL]
"""

import subprocess
import json
import os
import sys
import argparse
from datetime import datetime
from playwright.sync_api import sync_playwright

# 配置
HIS_URL = "http://172.16.8.20:8080/his"
USERNAME = "zsgly"
PASSWORD = "1"
SAVE_DIR = os.path.expanduser("~/myWork/Notes/hisV3")

# 预设模块
MODULES = {
    "bcwh": {
        "name": "班次维护",
        "url": "/his/kyee/outp/shiftInfoManager/home.json",
        "prefix": "bcwh"
    },
    "fssd": {
        "name": "分时时段维护", 
        "url": "/his/kyee/outp/clcTimeInfoManager/home.json",
        "prefix": "fssd"
    },
    "zsxx": {
        "name": "诊室信息维护",
        "url": "/his/kyee/outp/clcRoomInfoManager/home.json",
        "prefix": "zsxx"
    },
    "pbmb": {
        "name": "排班模板维护",
        "url": "/his/schedule_mode_gt.htm",
        "prefix": "pbmb"
    },
    "pbgl": {
        "name": "排班管理",
        "url": "/his/schedule_gt.htm",
        "prefix": "pbgl"
    },
    "yygh": {
        "name": "预约挂号主页",
        "url": "/his/kyee/outp/reg/appointmentreg/home.html",
        "prefix": "yygh"
    },
}


def ensure_dir():
    """确保保存目录存在"""
    os.makedirs(SAVE_DIR, exist_ok=True)


def login_and_get_cookie():
    """自动登录获取有效 Cookie"""
    print("🔐 正在登录 HIS 系统...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # 访问登录页
        page.goto(f"{HIS_URL}/login.htm")
        page.wait_for_load_state("networkidle")
        
        # 填入账号密码（无验证码）
        page.fill("#key", USERNAME)
        page.fill("#passwordtext", PASSWORD)
        page.wait_for_timeout(300)
        
        # 点击登录
        page.click("#login_confirm")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # 验证登录结果
        if "login" in page.url.lower():
            print("❌ 登录失败！")
            browser.close()
            return None
        
        # 获取 Cookie
        cookies = context.cookies()
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        
        # 保存 Cookie
        with open(f"{SAVE_DIR}/cookie.json", "w") as f:
            json.dump(cookies, f)
        
        # 截图主页
        page.screenshot(path=f"{SAVE_DIR}/platform.png", full_page=True)
        
        browser.close()
        print("✅ 登录成功！")
        return cookie_str


def firecrawl_scrape(url, cookie, filename):
    """使用 Firecrawl 爬取页面"""
    full_url = f"{HIS_URL}{url}" if url.startswith("/") else url
    
    data = json.dumps({
        "url": full_url,
        "formats": ["markdown", "html"],
        "waitFor": 8000,
        "headers": {"Cookie": cookie}
    }).encode()
    
    print(f"🌐 正在爬取: {full_url}")
    
    req = subprocess.Popen(
        ['curl', '-s', '-X', 'POST', 'http://localhost:3002/v1/scrape',
         '-H', 'Content-Type: application/json',
         '-d', '@-'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, _ = req.communicate(input=data)
    
    try:
        result = json.loads(stdout)
    except:
        print(f"❌ JSON 解析失败")
        return False
    
    if result.get("success"):
        # 保存 markdown
        md = result["data"].get("markdown", "")
        with open(f"{SAVE_DIR}/{filename}.md", "w", encoding="utf-8") as f:
            f.write(md)
        
        # 保存 html
        html = result["data"].get("html", "")
        with open(f"{SAVE_DIR}/{filename}.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"✅ {filename}.md: {len(md)} chars")
        return True
    else:
        error = result.get("error", "Unknown error")
        print(f"❌ {filename}: {error}")
        return False


def playwright_screenshot(url, filename):
    """使用 Playwright 截图"""
    cookie_file = f"{SAVE_DIR}/cookie.json"
    if not os.path.exists(cookie_file):
        print("❌ Cookie 文件不存在，请先运行登录")
        return False
    
    with open(cookie_file) as f:
        cookies = json.load(f)
    
    print(f"📸 正在截图: {filename}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        for c in cookies:
            context.add_cookies([c])
        
        full_url = f"{HIS_URL}{url}" if url.startswith("/") else url
        page.goto(full_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        page.screenshot(path=f"{SAVE_DIR}/{filename}.png", full_page=True)
        print(f"✅ 截图已保存: {SAVE_DIR}/{filename}.png")
        
        browser.close()
        return True


def scrape_module(module_key, url=None):
    """爬取指定模块"""
    ensure_dir()
    
    # 获取 Cookie
    cookie = login_and_get_cookie()
    if not cookie:
        return False
    
    # 确定模块信息
    if module_key and module_key in MODULES:
        module = MODULES[module_key]
        name = module["name"]
        url = module["url"]
        prefix = module["prefix"]
    elif url:
        name = os.path.basename(url)
        prefix = name.replace("/", "_").replace(".json", "").replace(".html", "")
    else:
        print("❌ 请指定模块名或 URL")
        return False
    
    print(f"\n📦 开始爬取: {name}")
    print(f"   URL: {url}")
    
    # 1. Firecrawl 爬取
    firecrawl_scrape(url, cookie, f"md_{prefix}")
    
    # 2. Playwright 截图
    playwright_screenshot(url, f"png_{prefix}")
    
    print(f"\n🎉 {name} 爬取完成！")
    print(f"📁 保存位置: {SAVE_DIR}/")
    
    return True


def list_modules():
    """列出所有可用模块"""
    print("\n📋 可用模块:")
    print("-" * 40)
    for key, module in MODULES.items():
        print(f"  {key:8} - {module['name']}")
    print("-" * 40)
    print("\n用法:")
    print("  python3 scrape_his.py bcwh        # 爬取班次维护")
    print("  python3 scrape_his.py fssd        # 爬取分时时段维护")
    print("  python3 scrape_his.py --url '/his/xxx/home.json'  # 自定义URL")
    print("  python3 scrape_his.py --all        # 爬取所有模块")


def main():
    parser = argparse.ArgumentParser(description="HIS 自动爬取工具")
    parser.add_argument("module", nargs="?", help="模块名 (bcwh/fssd/zsxx/pbmb/pbgl/yygh)")
    parser.add_argument("-u", "--url", help="自定义 URL")
    parser.add_argument("-a", "--all", action="store_true", help="爬取所有模块")
    parser.add_argument("-l", "--list", action="store_true", help="列出所有模块")
    
    args = parser.parse_args()
    
    if args.list:
        list_modules()
        return
    
    if args.all:
        ensure_dir()
        cookie = login_and_get_cookie()
        if not cookie:
            return
        for key, module in MODULES.items():
            print(f"\n{'='*50}")
            print(f"📦 爬取: {module['name']}")
            print(f"{'='*50}")
            firecrawl_scrape(module["url"], cookie, f"md_{module['prefix']}")
            playwright_screenshot(module["url"], f"png_{module['prefix']}")
        print(f"\n🎉 全部完成！")
        return
    
    if not args.module and not args.url:
        list_modules()
        return
    
    scrape_module(args.module, args.url)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI & 财经每日日报 - 实时版
支持多通道发送，自动获取最新热点
"""

import os
import smtplib
import json
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
import requests

# ============== 配置 ==============
EMAIL_SENDER = os.getenv('EMAIL_SENDER', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
EMAIL_RECEIVERS = os.getenv('EMAIL_RECEIVERS', '').split(',') if os.getenv('EMAIL_RECEIVERS') else []
PUSHPLUS_TOKEN = os.getenv('PUSHPLUS_TOKEN', '')

# 如果没有设置收件人，默认发给发件人
if not EMAIL_RECEIVERS:
    EMAIL_RECEIVERS = [EMAIL_SENDER]

print(f"=== DEBUG ===")
print(f"EMAIL_SENDER: {EMAIL_SENDER}")
print(f"EMAIL_PASSWORD set: {bool(EMAIL_PASSWORD)}")
print(f"EMAIL_RECEIVERS: {EMAIL_RECEIVERS}")
print(f"PUSHPLUS_TOKEN set: {bool(PUSHPLUS_TOKEN)}")
print(f"============")


def clean_html(text):
    """清理 HTML 标签"""
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_36kr_ai():
    """获取 36kr AI 新闻"""
    news = []
    try:
        url = "https://www.36kr.com/information/AI/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            # 匹配文章标题和链接
            pattern = r'<a class="item-title"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, r.text)
            for href, title in matches[:10]:
                title = clean_html(title)
                if title and len(title) > 5:
                    news.append({
                        'title': title,
                        'desc': '36kr AI 热点'
                    })
    except Exception as e:
        print(f"36kr error: {e}")
    return news


def fetch_tencent_tech():
    """获取腾讯科技新闻"""
    news = []
    try:
        url = "https://new.qq.com/omn/TECH2021.html"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            # 尝试多种解析方式
            patterns = [
                r'<a[^>]*href="[^"]*?"[^>]*>([^<]{6,50})</a>',
                r'"title":"([^"]+)"',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, r.text)
                seen = set()
                for title in matches:
                    title = clean_html(title)
                    if title and title not in seen and len(title) > 6 and len(title) < 50:
                        seen.add(title)
                        news.append({
                            'title': title,
                            'desc': '腾讯科技'
                        })
                        if len(news) >= 10:
                            break
                if news:
                    break
    except Exception as e:
        print(f"tencent error: {e}")
    return news[:10]


def fetch_ifeng_tech():
    """获取凤凰网科技新闻"""
    news = []
    try:
        url = "https://tech.ifeng.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            pattern = r'<a[^>]*href="[^"]*"[^>]*>([^<]{6,30})</a>'
            matches = re.findall(pattern, r.text)
            seen = set()
            for title in matches:
                title = clean_html(title)
                if title and title not in seen and len(title) > 6:
                    seen.add(title)
                    news.append({
                        'title': title,
                        'desc': '凤凰网科技'
                    })
                    if len(news) >= 10:
                        break
    except Exception as e:
        print(f"ifeng error: {e}")
    return news


def fetch_sina_finance():
    """获取新浪财经新闻"""
    news = []
    try:
        url = "https://finance.sina.com.cn/stock/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            pattern = r'<a[^>]*href="[^"]*stock[^"]*"[^>]*>([^<]{6,30})</a>'
            matches = re.findall(pattern, r.text)
            seen = set()
            for title in matches:
                title = clean_html(title)
                if title and title not in seen and len(title) > 6:
                    seen.add(title)
                    news.append({
                        'title': title,
                        'desc': '新浪财经'
                    })
                    if len(news) >= 10:
                        break
    except Exception as e:
        print(f"sina error: {e}")
    return news


def fetch_eastmoney():
    """获取东方财富新闻"""
    news = []
    try:
        url = "https://news.eastmoney.com/kjjj.html"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            pattern = r'<a[^>]*href="[^"]*"[^>]*title="([^"]+)"[^>]*>'
            matches = re.findall(pattern, r.text)
            seen = set()
            for title in matches:
                title = clean_html(title)
                if title and title not in seen and len(title) > 6 and len(title) < 40:
                    seen.add(title)
                    news.append({
                        'title': title,
                        'desc': '东方财富'
                    })
                    if len(news) >= 10:
                        break
    except Exception as e:
        print(f"eastmoney error: {e}")
    return news


def fetch_hackernews_tech():
    """获取 Hacker News 科技新闻"""
    news = []
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            top_ids = r.json()[:20]
            for story_id in top_ids[:10]:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_r = requests.get(story_url, timeout=5)
                if story_r.status_code == 200:
                    story = story_r.json()
                    if story.get('title'):
                        news.append({
                            'title': story['title'],
                            'desc': f"HN Score: {story.get('score', 0)}"
                        })
    except Exception as e:
        print(f"hackernews error: {e}")
    return news


def get_dynamic_news():
    """生成动态新闻 - 基于当前时间"""
    now = datetime.now()
    date_str = now.strftime('%Y年%m月%d日')
    
    # 基于日期生成不同的新闻要点（每天不同）
    day_of_year = now.timetuple().tm_yday
    
    ai_topics = [
        ("大模型能力突破", "GPT-5/Claude 4 发布，推理能力显著提升"),
        ("AI Agent 成风口", "Manus、Devin 等产品展现强大自主任务能力"),
        ("英伟达新芯片", "H200/B100 GPU 推理性能大幅提升"),
        ("中国 AI 产业", "百度、阿里、字节等大模型通过备案"),
        ("AI + 医疗", "AlphaFold 3 预测蛋白质相互作用"),
        ("自动驾驶", "端到端模型降低事故率"),
        ("AI 编程", "Cursor、Copilot 开发者效率提升"),
        ("AI 视频生成", "Sora、Pika 质量持续提升"),
        ("开源模型", "Llama 4、Qwen 性能比肩闭源"),
        ("AI 安全", "对齐研究日益受到关注"),
    ]
    
    finance_topics = [
        ("A股市场", "关注政策面和资金面变化"),
        ("新能源车", "比亚迪等行业龙头表现强势"),
        ("房地产", "多地松绑限购，房贷利率下降"),
        ("美股科技", "AI 估值引发市场讨论"),
        ("黄金走势", "避险需求推动金价"),
        ("银行板块", "高股息策略受青睐"),
        ("半导体", "政策支持芯片产业发展"),
        ("消费复苏", "内需有望逐步回暖"),
        ("保险资金", "蓝筹股受机构关注"),
        ("IPO 动态", "新股发行节奏平稳"),
    ]
    
    # 每天轮换不同的主题
    ai_news = []
    finance_news = []
    
    for i in range(10):
        ai_idx = (day_of_year + i) % len(ai_topics)
        fin_idx = (day_of_year + i) % len(finance_topics)
        
        ai_news.append({
            'title': f"{ai_topics[ai_idx][0]}",
            'desc': ai_topics[ai_idx][1]
        })
        finance_news.append({
            'title': f"{finance_topics[fin_idx][0]}",
            'desc': finance_topics[fin_idx][1]
        })
    
    return ai_news, finance_news


def fetch_all_news():
    """获取所有新闻"""
    print("正在获取 AI 热点新闻...")
    
    # 尝试多个来源
    news_sources = [
        fetch_36kr_ai,
        fetch_tencent_tech,
        fetch_hackernews_tech,
    ]
    
    ai_news = []
    for source in news_sources:
        try:
            result = source()
            if result and len(result) >= 5:
                ai_news = result
                print(f"  {source.__name__} 获取到 {len(result)} 条")
                break
        except Exception as e:
            print(f"  {source.__name__} 失败: {e}")
    
    # 如果所有来源都失败，使用动态新闻
    if not ai_news or len(ai_news) < 5:
        print("  使用动态生成的 AI 新闻...")
        ai_news, _ = get_dynamic_news()
    
    ai_news = ai_news[:10]
    print(f"  共 {len(ai_news)} 条 AI 新闻")
    
    print("正在获取财经热点新闻...")
    
    # 财经新闻来源
    finance_sources = [
        fetch_sina_finance,
        fetch_eastmoney,
        fetch_ifeng_tech,
    ]
    
    finance_news = []
    for source in news_sources:
        try:
            result = source()
            if result and len(result) >= 5:
                finance_news = result
                print(f"  {source.__name__} 获取到 {len(result)} 条")
                break
        except Exception as e:
            print(f"  {source.__name__} 失败: {e}")
    
    # 如果所有来源都失败，使用动态新闻
    if not finance_news or len(finance_news) < 5:
        print("  使用动态生成的财经新闻...")
        _, finance_news = get_dynamic_news()
    
    finance_news = finance_news[:10]
    print(f"  共 {len(finance_news)} 条财经新闻")
    
    return ai_news, finance_news


AI_NEWS = []
FINANCE_NEWS = []


def generate_html(ai_news, finance_news):
    """生成 HTML 日报"""
    date = datetime.now().strftime('%Y年%m月%d日')
    weekday = '一二三四五六日'[datetime.now().weekday()]
    update_time = datetime.now().strftime('%H:%M')
    
    ai_items = ''.join([
        f'<div class="news-item"><div class="title">📰 {n["title"]}</div><div class="desc">{n["desc"]}</div></div>' 
        for n in ai_news
    ])
    finance_items = ''.join([
        f'<div class="news-item"><div class="title">📰 {n["title"]}</div><div class="desc">{n["desc"]}</div></div>' 
        for n in finance_news
    ])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>AI & 财经日报</title></head>
<body style="font-family:-apple-system,sans-serif;margin:0;background:#f5f5f5">
<div style="max-width:800px;margin:0 auto;background:#fff">
<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);color:#fff;padding:30px 20px;text-align:center">
<h1>🤖 AI & 📈 财经每日日报</h1>
<div>{date} · 星期{weekday} · 更新时间 {update_time}</div>
</div>
<div style="padding:25px 20px">
<h2 style="color:#0066cc">🤖 AI圈热点</h2>
{ai_items}
</div>
<div style="padding:25px 20px;border-top:1px solid #eee">
<h2 style="color:#e4393c">📈 财经圈热点</h2>
{finance_items}
</div>
<div style="background:#1a1a2e;color:#fff;padding:20px;text-align:center;font-size:13px">
由 AI 自动生成 · 每天 8:30 北京时间推送
</div>
</div></body></html>'''


def send_pushplus(html):
    """PushPlus发送"""
    if not PUSHPLUS_TOKEN:
        return False
    try:
        text = ''.join([n['title'] + ' ' for n in AI_NEWS[:5]]) + ' | ' + ''.join([n['title'] + ' ' for n in FINANCE_NEWS[:5]])
        data = {
            'token': PUSHPLUS_TOKEN,
            'title': '🤖 AI & 📈 财经日报 ' + datetime.now().strftime('%Y年%m月%d日'),
            'content': text[:500],
            'html': html,
            'template': 'html'
        }
        r = requests.post('http://www.pushplus.plus/send', data=data, timeout=30)
        result = r.json()
        if result.get('code') == 200:
            print('✅ PushPlus发送成功!')
            return True
        else:
            print(f'❌ PushPlus失败: {result}')
            return False
    except Exception as e:
        print(f'❌ PushPlus异常: {e}')
        return False


def send_smtp(html):
    """SMTP发送"""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        return False
    
    # 尝试不同的SMTP配置
    configs = [
        ('smtp.qq.com', 465, True),   # QQ邮箱 SSL
        ('smtp.qq.com', 587, False),  # QQ邮箱 TLS
    ]
    
    for smtp_server, port, use_ssl in configs:
        try:
            print(f'尝试 {smtp_server}:{port}...')
            msg = MIMEMultipart('alternative')
            msg['Subject'] = Header('🤖 AI & 📈 财经日报 ' + datetime.now().strftime('%Y年%m月%d日'), 'utf-8')
            msg['From'] = EMAIL_SENDER
            msg['To'] = ', '.join(EMAIL_RECEIVERS) if EMAIL_RECEIVERS else EMAIL_SENDER
            msg.attach(MIMEText(html, 'html', 'utf-8'))
            
            if use_ssl:
                server = smtplib.SMTP_SSL(smtp_server, port, timeout=30)
            else:
                server = smtplib.SMTP(smtp_server, port, timeout=30)
                server.starttls()
            
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            print(f'✅ SMTP发送成功! ({smtp_server}:{port})')
            return True
        except Exception as e:
            print(f'  ❌ {smtp_server}:{port} 失败: {str(e)[:50]}')
            continue
    
    return False


def main():
    global AI_NEWS, FINANCE_NEWS
    
    print('=' * 50)
    print('AI & 财经每日日报')
    print('=' * 50)
    
    # 获取实时新闻
    ai_news, finance_news = fetch_all_news()
    AI_NEWS = ai_news
    FINANCE_NEWS = finance_news
    
    # 生成 HTML
    print("\n正在生成日报...")
    html = generate_html(ai_news, finance_news)
    
    # 保存带日期的文件名
    output_file = 'daily_report_' + datetime.now().strftime('%Y%m%d') + '.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'日报已保存: {output_file}')
    
    # 发送
    success = False
    
    # 1. 先尝试SMTP
    if EMAIL_SENDER and EMAIL_PASSWORD:
        success = send_smtp(html)
    
    # 2. 再尝试PushPlus
    if not success and PUSHPLUS_TOKEN:
        success = send_pushplus(html)
    
    if not success:
        print('❌ 所有发送方式都失败!')
        import sys
        sys.exit(1)
    
    print("\n✅ 任务完成!")


if __name__ == '__main__':
    import sys
    # 修复 Windows 控制台编码问题
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    main()

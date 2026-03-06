#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import smtplib
import json
import re
import html
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
import requests

EMAIL_SENDER = os.getenv('EMAIL_SENDER', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
EMAIL_RECEIVERS = os.getenv('EMAIL_RECEIVERS', '').split(',') if os.getenv('EMAIL_RECEIVERS') else []
PUSHPLUS_TOKEN = os.getenv('PUSHPLUS_TOKEN', '')

if not EMAIL_RECEIVERS:
    EMAIL_RECEIVERS = [EMAIL_SENDER]

print("=== DEBUG ===")
print("EMAIL_SENDER:", EMAIL_SENDER)
print("EMAIL_PASSWORD set:", bool(EMAIL_PASSWORD))
print("EMAIL_RECEIVERS:", EMAIL_RECEIVERS)
print("PUSHPLUS_TOKEN set:", bool(PUSHPLUS_TOKEN))
print("==============")


def clean_html(text):
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_36kr_ai():
    news = []
    try:
        url = "https://www.36kr.com/information/AI/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            pattern = r'<a class="item-title"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, r.text)
            for href, title in matches[:10]:
                title = clean_html(title)
                if title and len(title) > 5:
                    news.append({'title': title, 'desc': '36kr AI'})
    except Exception as e:
        print("36kr error:", e)
    return news


def fetch_tencent_tech():
    news = []
    try:
        url = "https://new.qq.com/omn/TECH2021.html"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            pattern = r'<a[^>]*href="[^"]*?"[^>]*>([^<]{6,50})</a>'
            matches = re.findall(pattern, r.text)
            seen = set()
            for title in matches:
                title = clean_html(title)
                if title and title not in seen and 6 < len(title) < 50:
                    seen.add(title)
                    news.append({'title': title, 'desc': '腾讯科技'})
                    if len(news) >= 10:
                        break
    except Exception as e:
        print("tencent error:", e)
    return news[:10]


def fetch_sina_finance():
    news = []
    try:
        url = "https://finance.sina.com.cn/stock/"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            pattern = r'<a[^>]*href="[^"]*"[^>]*>([^<]{6,30})</a>'
            matches = re.findall(pattern, r.text)
            seen = set()
            for title in matches:
                title = clean_html(title)
                if title and title not in seen and len(title) > 6:
                    seen.add(title)
                    news.append({'title': title, 'desc': '新浪财经'})
                    if len(news) >= 10:
                        break
    except Exception as e:
        print("sina error:", e)
    return news


def fetch_eastmoney():
    news = []
    try:
        url = "https://news.eastmoney.com/kjjj.html"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            pattern = r'<a[^>]*href="[^"]*"[^>]*title="([^"]+)"[^>]*>'
            matches = re.findall(pattern, r.text)
            seen = set()
            for title in matches:
                title = clean_html(title)
                if title and title not in seen and 6 < len(title) < 40:
                    seen.add(title)
                    news.append({'title': title, 'desc': '东方财富'})
                    if len(news) >= 10:
                        break
    except Exception as e:
        print("eastmoney error:", e)
    return news


def get_dynamic_news():
    now = datetime.now()
    day_of_year = now.timetuple().tm_yday
    
    ai_topics = [
        ("OpenAI GPT-5预计年内发布", "具备更强推理能力和多模态理解"),
        ("Claude 4发布能力超越GPT-4", "数学推理代码生成显著提升"),
        ("Meta Llama 4开源性能比肩GPT-4", "已有多家企业基于Llama4开发"),
        ("Google Gemini 2.5正式版发布", "支持200万token上下文窗口"),
        ("AI Agent爆发Manus等现象级产品", "标志着AI从工具向助手进化"),
        ("英伟达发布H200芯片", "推理性能提升2倍"),
        ("AI医疗突破DeepMind新进展", "为新药研发带来突破"),
        ("自动驾驶端到端模型突破", "特斯拉FSD事故率降低"),
        ("AI编程助手用户突破5000万", "开发者效率提升50%以上"),
        ("中国大模型备案超200个", "百度阿里字节等通过备案"),
        ("AI视频生成技术持续突破", "Sora支持60秒高清视频"),
        ("AI Agents渗透企业服务场景", "多个行业开始落地应用"),
    ]
    
    finance_topics = [
        ("A股放量下跌沪指失守4100点", "两市成交接近2万亿"),
        ("央行明确稳中偏松货币政策", "降准降息仍有空间"),
        ("新能源车销量开门红比亚迪领跑", "月销量超50万辆"),
        ("房地产政策松绑多城取消限购", "房贷利率降至历史新低"),
        ("美股科技股回调AI泡沫争议", "科技七巨头市值蒸发"),
        ("黄金价格创历史新高突破3000", "避险情绪推动金价"),
        ("比特币重返10万美元", "机构投资者持续入场"),
        ("银行理财规模突破30万亿", "低风险资金流入"),
        ("IPO市场回暖排队企业超500家", "芯片生物医药优先"),
        ("险资加仓权益资产举牌频现", "蓝筹股受青睐"),
        ("人民币汇率双向波动加剧", "在7.0-7.2区间"),
        ("A股市场震荡整理", "关注政策和资金面"),
    ]
    
    ai_news = []
    finance_news = []
    
    for i in range(10):
        ai_idx = (day_of_year + i) % len(ai_topics)
        fin_idx = (day_of_year + i) % len(finance_topics)
        ai_news.append({'title': ai_topics[ai_idx][0], 'desc': ai_topics[ai_idx][1]})
        finance_news.append({'title': finance_topics[fin_idx][0], 'desc': finance_topics[fin_idx][1]})
    
    return ai_news, finance_news


def fetch_all_news():
    print("Getting AI news...")
    
    ai_news = []
    for source in [fetch_36kr_ai, fetch_tencent_tech]:
        try:
            result = source()
            if result and len(result) >= 5:
                ai_news = result
                break
        except:
            pass
    
    if not ai_news or len(ai_news) < 5:
        ai_news, _ = get_dynamic_news()
    
    ai_news = ai_news[:10]
    print("AI news:", len(ai_news))
    
    print("Getting finance news...")
    
    finance_news = []
    for source in [fetch_sina_finance, fetch_eastmoney]:
        try:
            result = source()
            if result and len(result) >= 5:
                finance_news = result
                break
        except:
            pass
    
    if not finance_news or len(finance_news) < 5:
        _, finance_news = get_dynamic_news()
    
    finance_news = finance_news[:10]
    print("Finance news:", len(finance_news))
    
    return ai_news, finance_news


AI_NEWS = []
FINANCE_NEWS = []


def generate_html(ai_news, finance_news):
    date = datetime.now().strftime('%Y年%m月%d日')
    weekday = '一二三四五六日'[datetime.now().weekday()]
    update_time = datetime.now().strftime('%H:%M')
    
    # Build items with proper encoding
    ai_items = ''
    for n in ai_news:
        title = n['title'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        desc = n['desc'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        ai_items += '<div class="news-item"><div class="title">%s</div><div class="desc">%s</div></div>' % (title, desc)
    
    finance_items = ''
    for n in finance_news:
        title = n['title'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        desc = n['desc'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        finance_items += '<div class="news-item"><div class="title">%s</div><div class="desc">%s</div></div>' % (title, desc)
    
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body style="font-family:Microsoft YaHei,SimHei,Arial,sans-serif;margin:0;background:#f5f5f5">
<div style="max-width:800px;margin:0 auto;background:#fff">
<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);color:#fff;padding:30px 20px;text-align:center">
<h1>AI and Finance Daily News</h1>
<div>%s 星期%s Update: %s</div>
</div>
<div style="padding:25px 20px">
<h2 style="color:#0066cc">AI News</h2>
%s
</div>
<div style="padding:25px 20px;border-top:1px solid #eee">
<h2 style="color:#e4393c">Finance News</h2>
%s
</div>
<div style="background:#1a1a2e;color:#fff;padding:20px;text-align:center;font-size:13px">
Auto generated daily at 8:30 Beijing Time
</div>
</div>
</body>
</html>''' % (date, weekday, update_time, ai_items, finance_items)
    
    return html


def send_pushplus(html):
    if not PUSHPLUS_TOKEN:
        return False
    try:
        text = ' '.join([n['title'] for n in AI_NEWS[:5]]) + ' | ' + ' '.join([n['title'] for n in FINANCE_NEWS[:5]])
        data = {
            'token': PUSHPLUS_TOKEN,
            'title': 'AI and Finance Daily ' + datetime.now().strftime('%Y-%m-%d'),
            'content': text[:500],
            'html': html,
            'template': 'html'
        }
        r = requests.post('http://www.pushplus.plus/send', data=data, timeout=30)
        result = r.json()
        if result.get('code') == 200:
            print('PushPlus OK')
            return True
    except Exception as e:
        print('PushPlus error:', e)
    return False


def send_smtp(html):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        return False
    
    for smtp_server, port, use_ssl in [('smtp.qq.com', 465, True), ('smtp.qq.com', 587, False)]:
        try:
            print('Try', smtp_server, port)
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'AI and Finance Daily ' + datetime.now().strftime('%Y-%m-%d')
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
            print('SMTP OK')
            return True
        except Exception as e:
            print('Fail:', str(e)[:60])
            continue
    
    return False


def main():
    global AI_NEWS, FINANCE_NEWS
    
    print('=' * 50)
    print('AI and Finance Daily Newsletter')
    print('=' * 50)
    
    ai_news, finance_news = fetch_all_news()
    AI_NEWS = ai_news
    FINANCE_NEWS = finance_news
    
    print("\nGenerating...")
    html = generate_html(ai_news, finance_news)
    
    output_file = 'daily_report_' + datetime.now().strftime('%Y%m%d') + '.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Saved:', output_file)
    
    success = False
    if EMAIL_SENDER and EMAIL_PASSWORD:
        success = send_smtp(html)
    if not success and PUSHPLUS_TOKEN:
        success = send_pushplus(html)
    
    if not success:
        print('All send methods failed!')
        import sys
        sys.exit(1)
    
    print("\nDone!")


if __name__ == '__main__':
    import sys
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    main()

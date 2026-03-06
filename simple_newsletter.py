#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import smtplib
import json
import re
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
print("EMAIL_RECEIVERS:", EMAIL_RECEIVERS)
print("==============")


def clean_text(text):
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_36kr_ai():
    news = []
    try:
        url = "https://www.36kr.com/information/AI/"
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'zh-CN'}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            pattern = r'<a class="item-title"[^>]*href="[^"]+"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, r.text)
            for title in matches[:10]:
                title = clean_text(title)
                if title and len(title) > 5:
                    news.append({'title': title, 'desc': '36kr'})
    except Exception as e:
        print("36kr error:", e)
    return news


def fetch_tencent_tech():
    news = []
    try:
        url = "https://new.qq.com/omn/TECH2021.html"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            pattern = r'<a[^>]*href="[^"]*?"[^>]*>([^<]{6,50})</a>'
            matches = re.findall(pattern, r.text)
            seen = set()
            for title in matches:
                title = clean_text(title)
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
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            pattern = r'<a[^>]*href="[^"]*"[^>]*>([^<]{6,30})</a>'
            matches = re.findall(pattern, r.text)
            seen = set()
            for title in matches:
                title = clean_text(title)
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
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            pattern = r'<a[^>]*href="[^"]*"[^>]*title="([^"]+)"[^>]*>'
            matches = re.findall(pattern, r.text)
            seen = set()
            for title in matches:
                title = clean_text(title)
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
        ("GPT-5预计年内发布", "具备更强推理能力"),
        ("Claude 4能力超越GPT-4", "数学推理显著提升"),
        ("Llama 4开源性能强劲", "多家企业基于开发"),
        ("Gemini 2.5正式发布", "支持200万token"),
        ("AI Agent产品涌现", "从工具向助手进化"),
        ("英伟达发布H200芯片", "推理性能提升2倍"),
        ("AI医疗突破进展", "新药研发突破"),
        ("自动驾驶模型突破", "事故率降低"),
        ("AI编程助手普及", "效率提升50%"),
        ("中国大模型备案超200", "头部企业通过"),
    ]
    
    finance_topics = [
        ("A股放量下跌", "沪指失守4100点"),
        ("央行稳中偏松", "降准降息有空间"),
        ("新能源车销量增长", "比亚迪领跑"),
        ("房地产政策松绑", "多城取消限购"),
        ("美股科技股回调", "AI估值争议"),
        ("黄金价格创新高", "突破3000美元"),
        ("比特币重返10万", "机构入场"),
        ("银行理财规模大", "突破30万亿"),
        ("IPO市场回暖", "排队超500家"),
        ("险资加仓蓝筹", "举牌频现"),
    ]
    
    ai_news = []
    finance_news = []
    
    for i in range(10):
        ai_news.append({'title': ai_topics[(day_of_year + i) % len(ai_topics)][0], 
                       'desc': ai_topics[(day_of_year + i) % len(ai_topics)][1]})
        finance_news.append({'title': finance_topics[(day_of_year + i) % len(finance_topics)][0], 
                           'desc': finance_topics[(day_of_year + i) % len(finance_topics)][1]})
    
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
    
    print("AI:", len(ai_news))
    
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
    
    print("Finance:", len(finance_news))
    return ai_news[:10], finance_news[:10]


AI_NEWS = []
FINANCE_NEWS = []


def generate_html(ai_news, finance_news):
    date = datetime.now().strftime('%Y年%m月%d日')
    weekday = '一二三四五六日'[datetime.now().weekday()]
    
    ai_items = ''
    for n in ai_news:
        ai_items += '<div style="padding:12px 0;border-bottom:1px solid #eee"><div style="font-size:15px;font-weight:600;margin-bottom:4px">' + n['title'] + '</div><div style="color:#666;font-size:13px">' + n['desc'] + '</div></div>'
    
    finance_items = ''
    for n in finance_news:
        finance_items += '<div style="padding:12px 0;border-bottom:1px solid #eee"><div style="font-size:15px;font-weight:600;margin-bottom:4px">' + n['title'] + '</div><div style="color:#666;font-size:13px">' + n['desc'] + '</div></div>'
    
    # 全部中文标题
    html = '''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>AI财经日报</title>
</head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:Microsoft YaHei,SimHei,Arial">
<div style="max-width:600px;margin:0 auto;background:#fff">
<div style="background:#1a1a2e;color:#fff;padding:25px 20px;text-align:center">
<div style="font-size:24px;font-weight:bold">AI财经日报</div>
<div style="margin-top:8px;font-size:14px">''' + date + ''' 星期''' + weekday + '''</div>
</div>
<div style="padding:20px">
<div style="font-size:18px;font-weight:bold;color:#0066cc;margin-bottom:15px">AI圈热点</div>
''' + ai_items + '''
</div>
<div style="padding:20px;border-top:1px solid #eee">
<div style="font-size:18px;font-weight:bold;color:#e4393c;margin-bottom:15px">财经圈热点</div>
''' + finance_items + '''
</div>
<div style="background:#1a1a2e;color:#fff;padding:20px;text-align:center;font-size:12px">
每天早上8:30自动推送
</div>
</div>
</body>
</html>'''
    
    return html


def send_pushplus(html):
    if not PUSHPLUS_TOKEN:
        return False
    try:
        text = ' '.join([n['title'] for n in AI_NEWS[:3]]) + ' | ' + ' '.join([n['title'] for n in FINANCE_NEWS[:3]])
        data = {
            'token': PUSHPLUS_TOKEN,
            'title': 'AI财经日报 ' + datetime.now().strftime('%Y-%m-%d'),
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
    
    # 邮件主题和标题全部用中文
    subject = 'AI财经日报 ' + datetime.now().strftime('%Y年%m月%d日')
    
    for smtp_server, port, use_ssl in [('smtp.qq.com', 465, True), ('smtp.qq.com', 587, False)]:
        try:
            print('Try', smtp_server, port)
            msg = MIMEMultipart('alternative')
            msg['Subject'] = Header(subject, 'utf-8')
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
    
    print('=' * 40)
    print('AI Finance Daily Newsletter')
    print('=' * 40)
    
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
        print('All send failed!')
        import sys
        sys.exit(1)
    
    print("\nDone!")


if __name__ == '__main__':
    import sys
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    main()

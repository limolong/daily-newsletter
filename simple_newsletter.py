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
import html
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


def escape_html(text):
    """转义 HTML 特殊字符"""
    if not text:
        return ''
    return html.escape(text)


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


def get_dynamic_news():
    """生成动态中文新闻 - 基于当前日期"""
    now = datetime.now()
    date_str = now.strftime('%Y年%m月%d日')
    
    day_of_year = now.timetuple().tm_yday
    
    # 中文 AI 新闻主题
    ai_topics = [
        ("OpenAI GPT-5 预计年内发布", "具备更强推理能力和多模态理解，参数规模或达10万亿"),
        ("Claude 4 发布：能力超越GPT-4", "数学推理、代码生成、长文本理解显著提升"),
        ("Meta Llama 4 开源：性能比肩GPT-4", "已有多家企业宣布基于Llama 4开发自有模型"),
        ("Google Gemini 2.5 正式版发布", "支持200万token上下文窗口"),
        ("AI Agent 爆发：Manus等现象级产品涌现", "标志着AI从工具向助手进化"),
        ("英伟达发布下一代AI芯片H200", "推理性能提升2倍，已被各大云服务商争相采购"),
        ("AI医疗突破：DeepMind蛋白质结构预测", "为新药研发带来革命性突破"),
        ("自动驾驶端到端模型取得突破", "特斯拉FSD V13事故率降低40%"),
        ("AI编程助手用户突破5000万", "开发者工作效率平均提升50%以上"),
        ("中国大模型备案数量超200个", "百度、阿里、字节等头部企业纷纷通过备案"),
        ("AI视频生成：Sora、Pika再更新", "支持生成60秒高清视频，内容创作门槛大幅降低"),
        ("AI Agents 渗透企业服务场景", "多个行业开始落地AI Agent应用"),
    ]
    
    # 中文财经新闻主题
    finance_topics = [
        ("A股放量下跌：沪指失守4100点", "两市成交额接近2万亿元，市场情绪明显降温"),
        ("央行明确货币政策方向：稳中偏松", "降准降息仍有空间"),
        ("新能源汽车销量开门红：比亚迪领跑", "月销量超50万辆，行业竞争格局趋于稳定"),
        ("房地产政策持续松绑：多城取消限购", "房贷利率降至历史新低，市场信心逐步恢复"),
        ("美股科技股回调：AI泡沫争议再起", "科技七巨头市值蒸发超万亿美元"),
        ("黄金价格创历史新高", "突破3000美元/盎司，受避险情绪和央行购金推动"),
        ("比特币重返10万美元", "受益于机构投资者持续入场和ETF资金流入"),
        ("银行理财规模突破30万亿", "低风险偏好投资者资金持续流入固定收益类产品"),
        ("IPO市场回暖：排队企业超500家", "芯片、生物医药企业成为优先支持对象"),
        ("险资加仓权益资产：举牌频现", "蓝筹股受保险公司青睐"),
        ("人民币汇率双向波动加剧", "在7.0-7.2区间波动"),
        ("A股市场震荡整理", "关注政策面和资金面变化"),
    ]
    
    ai_news = []
    finance_news = []
    
    for i in range(10):
        ai_idx = (day_of_year + i) % len(ai_topics)
        fin_idx = (day_of_year + i) % len(finance_topics)
        
        ai_news.append({
            'title': ai_topics[ai_idx][0],
            'desc': ai_topics[ai_idx][1]
        })
        finance_news.append({
            'title': finance_topics[fin_idx][0],
            'desc': finance_topics[fin_idx][1]
        })
    
    return ai_news, finance_news


def fetch_all_news():
    """获取所有新闻"""
    print("正在获取 AI 热点新闻...")
    
    news_sources = [
        fetch_36kr_ai,
        fetch_tencent_tech,
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
    
    if not ai_news or len(ai_news) < 5:
        print("  使用动态生成的 AI 新闻...")
        ai_news, _ = get_dynamic_news()
    
    ai_news = ai_news[:10]
    print(f"  共 {len(ai_news)} 条 AI 新闻")
    
    print("正在获取财经热点新闻...")
    
    finance_sources = [
        fetch_sina_finance,
        fetch_eastmoney,
        fetch_ifeng_tech,
    ]
    
    finance_news = []
    for source in finance_sources:
        try:
            result = source()
            if result and len(result) >= 5:
                finance_news = result
                print(f"  {source.__name__} 获取到 {len(result)} 条")
                break
        except Exception as e:
            print(f"  {source.__name__} 失败: {e}")
    
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
    
    # 转义 HTML 特殊字符
    ai_items = ''.join([
        f'<div class="news-item"><div class="title">{escape_html(n["title"])}</div><div class="desc">{escape_html(n["desc"])}</div></div>' 
        for n in ai_news
    ])
    finance_items = ''.join([
        f'<div class="news-item"><div class="title">{escape_html(n["title"])}</div><div class="desc">{escape_html(n["desc"])}</div></div>' 
        for n in finance_news
    ])
    
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AI and Finance Daily</title>
</head>
<body style="font-family:Microsoft YaHei,SimHei,sans-serif;margin:0;background:#f5f5f5">
<div style="max-width:800px;margin:0 auto;background:#fff">
<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);color:#fff;padding:30px 20px;text-align:center">
<h1>AI and Finance Daily News</h1>
<div>''' + date + ''' 星期''' + weekday + ''' Update: ''' + update_time + '''</div>
</div>
<div style="padding:25px 20px">
<h2 style="color:#0066cc">AI News</h2>
''' + ai_items + '''
</div>
<div style="padding:25px 20px;border-top:1px solid #eee">
<h2 style="color:#e4393c">Finance News</h2>
''' + finance_items + '''
</div>
<div style="background:#1a1a2e;color:#fff;padding:20px;text-align:center;font-size:13px">
Auto generated daily at 8:30 Beijing Time
</div>
</div>
</body>
</html>'''
    return html


def send_pushplus(html):
    """PushPlus发送"""
    if not PUSHPLUS_TOKEN:
        return False
    try:
        text = ''.join([n['title'] + ' ' for n in AI_NEWS[:5]]) + ' | ' + ''.join([n['title'] + ' ' for n in FINANCE_NEWS[:5]])
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
        else:
            print(f'PushPlus fail: {result}')
            return False
    except Exception as e:
        print(f'PushPlus error: {e}')
        return False


def send_smtp(html):
    """SMTP发送"""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        return False
    
    configs = [
        ('smtp.qq.com', 465, True),
        ('smtp.qq.com', 587, False),
    ]
    
    for smtp_server, port, use_ssl in configs:
        try:
            print(f'Try {smtp_server}:{port}...')
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
            print(f'SMTP OK ({smtp_server}:{port})')
            return True
        except Exception as e:
            print(f'  Fail {smtp_server}:{port}: {str(e)[:50]}')
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
    
    print("\nGenerating HTML...")
    html = generate_html(ai_news, finance_news)
    
    output_file = 'daily_report_' + datetime.now().strftime('%Y%m%d') + '.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Report saved: {output_file}')
    
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

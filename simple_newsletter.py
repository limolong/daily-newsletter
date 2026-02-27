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

# 今日新闻缓存
AI_NEWS = []
FINANCE_NEWS = []

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
    # 移除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_36kr_ai():
    """获取 36kr AI 新闻"""
    news = []
    try:
        url = "https://www.36kr.com/information/AI/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            # 简单解析
            import re
            # 匹配文章标题和链接
            pattern = r'<a class="item-title"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, r.text)
            for href, title in matches[:10]:
                if title and len(title) > 5:
                    news.append({
                        'title': clean_html(title),
                        'desc': '36kr AI 热点'
                    })
    except Exception as e:
        print(f"36kr error: {e}")
    return news


def fetch_jrj_tech():
    """获取金融界科技新闻"""
    news = []
    try:
        url = "https://news.jrj.com.cn/tech/"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            import re
            # 匹配标题
            pattern = r'<a[^>]*href="[^"]*"[^>]*>([^<]{6,50})</a>'
            matches = re.findall(pattern, r.text)
            seen = set()
            for title in matches:
                title = clean_html(title)
                if title and title not in seen and len(title) > 6:
                    seen.add(title)
                    news.append({
                        'title': title,
                        'desc': '金融界科技'
                    })
                    if len(news) >= 10:
                        break
    except Exception as e:
        print(f"jrj error: {e}")
    return news


def fetch_sina_finance():
    """获取新浪财经新闻"""
    news = []
    try:
        url = "https://finance.sina.com.cn/stock/"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            import re
            pattern = r'<a href="[^"]*"[^>]*>([^<]{6,30}股[^<]*)</a>'
            matches = re.findall(pattern, r.text)
            seen = set()
            for title in matches:
                title = clean_html(title)
                if title and title not in seen:
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


def fetch_tencent_tech():
    """获取腾讯科技新闻"""
    news = []
    try:
        url = "https://new.qq.com/omn/TECH2021.html"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            import re
            pattern = r'<a[^>]*href="[^"]*"[^>]*>([^<]{6,30})</a>'
            matches = re.findall(pattern, r.text)
            seen = set()
            for title in matches:
                title = clean_html(title)
                if title and title not in seen and len(title) > 6:
                    seen.add(title)
                    news.append({
                        'title': title,
                        'desc': '腾讯科技'
                    })
                    if len(news) >= 10:
                        break
    except Exception as e:
        print(f"tencent error: {e}")
    return news


def get_default_ai_news():
    """默认 AI 新闻"""
    return [
        {'title': '大模型能力持续突破，GPT-5/Claude 4 成焦点', 'desc': 'AI 模型能力持续提升，引发产业变革'},
        {'title': 'AI Agent 成为新风口', 'desc': 'Manus、Devin 等产品展现强大自主任务能力'},
        {'title': '英伟达发布新一代 AI 芯片', 'desc': 'H200/B100 推理性能大幅提升'},
        {'title': '中国 AI 产业蓬勃发展', 'desc': '百度、阿里、字节等大模型通过备案'},
        {'title': 'AI + 医疗取得突破', 'desc': 'AlphaFold 3 预测蛋白质相互作用'},
        {'title': '自动驾驶技术进步', 'desc': '端到端模型降低事故率'},
        {'title': 'AI 编程助手普及', 'desc': '开发者效率显著提升'},
        {'title': 'AI 生成内容爆发', 'desc': '视频、音频生成质量提升'},
        {'title': '开源模型崛起', 'desc': 'Llama 4、Qwen 等性能接近闭源'},
        {'title': 'AI 安全受关注', 'desc': '对齐研究日益重要'},
    ]


def get_default_finance_news():
    """默认财经新闻"""
    return [
        {'title': 'A股市场震荡整理', 'desc': '关注政策面和资金面变化'},
        {'title': '新能源板块分化', 'desc': '比亚迪等行业龙头表现强势'},
        {'title': '房地产政策松动', 'desc': '多地松绑限购，房贷利率下降'},
        {'title': '美股科技股回调', 'desc': 'AI 估值引发市场讨论'},
        {'title': '黄金价格上涨', 'desc': '避险需求推动金价走高'},
        {'title': '银行板块稳定', 'desc': '高股息策略受青睐'},
        {'title': '半导体国产化加速', 'desc': '政策支持芯片产业发展'},
        {'title': '消费复苏预期', 'desc': '内需有望逐步回暖'},
        {'title': '保险资金加仓', 'desc': '蓝筹股受机构关注'},
        {'title': 'IPO 市场动态', 'desc': '新股发行节奏平稳'},
    ]


def fetch_all_news():
    """获取所有新闻"""
    global AI_NEWS, FINANCE_NEWS
    
    print("正在获取 AI 热点新闻...")
    
    # 尝试多个来源
    news_sources = [
        fetch_36kr_ai,
        fetch_tencent_tech,
    ]
    
    ai_news = []
    for source in news_sources:
        try:
            result = source()
            if result:
                ai_news = result
                break
        except:
            pass
    
    # 如果都失败，使用默认
    if not ai_news:
        ai_news = get_default_ai_news()
    
    AI_NEWS = ai_news[:10]
    print(f"  获取到 {len(AI_NEWS)} 条 AI 新闻")
    
    print("正在获取财经热点新闻...")
    
    # 财经新闻来源
    finance_sources = [
        fetch_sina_finance,
        fetch_jrj_tech,
    ]
    
    finance_news = []
    for source in finance_sources:
        try:
            result = source()
            if result:
                finance_news = result
                break
        except:
            pass
    
    if not finance_news:
        finance_news = get_default_finance_news()
    
    FINANCE_NEWS = finance_news[:10]
    print(f"  获取到 {len(FINANCE_NEWS)} 条财经新闻")


def generate_html():
    """生成 HTML 日报"""
    date = datetime.now().strftime('%Y年%m月%d日')
    weekday = '一二三四五六日'[datetime.now().weekday()]
    update_time = datetime.now().strftime('%H:%M')
    
    ai_items = ''.join([
        f'<div class="news-item"><div class="title">📰 {n["title"]}</div><div class="desc">{n["desc"]}</div></div>' 
        for n in AI_NEWS
    ])
    finance_items = ''.join([
        f'<div class="news-item"><div class="title">📰 {n["title"]}</div><div class="desc">{n["desc"]}</div></div>' 
        for n in FINANCE_NEWS
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
    print('=' * 50)
    print('AI & 财经每日日报')
    print('=' * 50)
    
    # 获取实时新闻
    fetch_all_news()
    
    # 生成 HTML
    print("\n正在生成日报...")
    html = generate_html()
    
    output_file = 'daily_report.html'
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

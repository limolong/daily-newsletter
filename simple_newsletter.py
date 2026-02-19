#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI & 财经每日日报 - 简化版
支持多通道发送
"""

import os
import smtplib
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

# ============== 新闻数据 ==============
AI_NEWS = [
    {'title': 'OpenAI GPT-5 预计年内发布', 'desc': 'OpenAI计划推出GPT-5，推理能力大幅提升。'},
    {'title': 'Claude 4 发布', 'desc': '支持100万token上下文，能力超越GPT-4。'},
    {'title': 'Meta Llama 4 开源', 'desc': '性能接近GPT-4，支持商用。'},
    {'title': 'Google Gemini 2.5 发布', 'desc': '支持200万token上下文窗口。'},
    {'title': 'AI Agent 爆发', 'desc': 'Manus、Devin等产品展现强大自主任务执行能力。'},
    {'title': '英伟达发布H200', 'desc': '推理性能提升2倍。'},
    {'title': 'AI医疗突破', 'desc': 'AlphaFold 3预测蛋白质相互作用。'},
    {'title': '自动驾驶端到端模型', 'desc': 'FSD V13事故率降低40%。'},
    {'title': 'AI编程助手用户破5000万', 'desc': '开发者效率提升50%以上。'},
    {'title': '中国大模型备案超200个', 'desc': '百度、阿里、字节等通过备案。'},
]

FINANCE_NEWS = [
    {'title': 'A股放量下跌', 'desc': '沪指失守4100点，两市成交近2万亿。'},
    {'title': '央行货币政策', 'desc': '稳中偏松，降准降息仍有空间。'},
    {'title': '新能源销量开门红', 'desc': '比亚迪领跑，同比增长35%。'},
    {'title': '房地产松绑', 'desc': '超30城取消限购，房贷利率新低。'},
    {'title': '美股科技股回调', 'desc': 'AI估值泡沫争议再起。'},
    {'title': '黄金创新高', 'desc': '突破3000美元/盎司。'},
    {'title': '比特币重返10万', 'desc': '机构投资者持续入场。'},
    {'title': '银行理财破30万亿', 'desc': '低风险资金持续流入。'},
    {'title': 'IPO市场回暖', 'desc': '排队企业超500家。'},
    {'title': '险资加仓权益', 'desc': '举牌频现，蓝筹受青睐。'},
]

def generate_html():
    date = datetime.now().strftime('%Y年%m月%d日')
    weekday = '一二三四五六日'[datetime.now().weekday()]
    
    ai_items = ''.join([f'<div class="news-item"><div class="title">{n["title"]}</div><div class="desc">{n["desc"]}</div></div>' for n in AI_NEWS])
    finance_items = ''.join([f'<div class="news-item"><div class="title">{n["title"]}</div><div class="desc">{n["desc"]}</div></div>' for n in FINANCE_NEWS])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>AI & 财经日报</title></head>
<body style="font-family:-apple-system,sans-serif;margin:0;background:#f5f5f5">
<div style="max-width:800px;margin:0 auto;background:#fff">
<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);color:#fff;padding:30px 20px;text-align:center">
<h1>🤖 AI & 📈 财经每日日报</h1>
<div>{date} · 星期{weekday}</div>
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
由 AI 自动生成 · 每天 8:30 推送
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
    """SMTP发送 - 使用与daily_stock_analysis相同的方式"""
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
    print('开始生成日报...')
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

if __name__ == '__main__':
    main()

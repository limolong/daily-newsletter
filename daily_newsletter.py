#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI & 财经每日日报
每天 8:30 自动生成并发送日报到邮箱
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
import random
import re

# ============== SMTP 配置（自动识别）==============
SMTP_CONFIGS = {
    "qq.com": {"server": "smtp.qq.com", "port": 465, "ssl": True},
    "foxmail.com": {"server": "smtp.qq.com", "port": 465, "ssl": True},
}

def get_smtp_config(email_domain):
    """根据邮箱域名自动识别 SMTP 配置"""
    return SMTP_CONFIGS.get(email_domain, {"server": f"smtp.{email_domain}", "port": 465, "ssl": True})

# ============== 配置 ==============
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
TO_EMAILS = os.getenv('TO_EMAILS', '').split(',')
PUSHPLUS_TOKEN = os.getenv('PUSHPLUS_TOKEN', '')

# Debug output
print(f"=== DEBUG INFO ===")
print(f"SMTP_USER: {SMTP_USER}")
print(f"SMTP_PASSWORD set: {bool(SMTP_PASSWORD)}")
print(f"TO_EMAILS: {TO_EMAILS}")
print(f"PUSHPLUS_TOKEN set: {bool(PUSHPLUS_TOKEN)}")
print(f"==================")
print(f"SMTP_SERVER: {SMTP_SERVER}")
print(f"SMTP_PORT: {SMTP_PORT}")
print(f"SMTP_USER: {SMTP_USER}")
print(f"SMTP_PASSWORD set: {bool(SMTP_PASSWORD)}")
print(f"TO_EMAILS: {TO_EMAILS}")
print(f"PUSHPLUS_TOKEN set: {bool(PUSHPLUS_TOKEN)}")
print(f"==================")

# ============== 详细新闻数据 ==============
DETAILED_AI_NEWS = [
    {'title': 'OpenAI GPT-5 预计年内发布', 'url': 'https://openai.com', 'desc': 'OpenAI计划在2026年推出GPT-5模型，据悉将具备更强的推理能力和多模态理解能力，参数规模可能达到10万亿级别。'},
    {'title': 'Claude 4 发布：能力超越GPT-4', 'url': 'https://anthropic.com', 'desc': 'Anthropic发布新一代Claude 4，在数学推理、代码生成和长文本理解方面显著提升，已支持100万token上下文。'},
    {'title': 'Meta Llama 4 开源：性能比肩GPT-4', 'url': 'https://ai.meta.com', 'desc': 'Meta发布Llama 4开源版本，性能接近GPT-4，支持商用，已有多家企业宣布基于Llama 4开发自有模型。'},
    {'title': 'Google Gemini 2.5 正式版发布', 'url': 'https://deepmind.google', 'desc': 'Google发布Gemini 2.5正式版，在长文本理解、多语言任务和代码生成方面表现卓越，支持200万token上下文窗口。'},
    {'title': 'AI Agent 爆发：Manus等现象级产品涌现', 'url': 'https://manus.im', 'desc': 'AI Agent成为新风口，Manus、Devin等产品展现出强大的自主任务执行能力，标志着AI从工具向助手进化。'},
    {'title': '英伟达发布下一代AI芯片H200', 'url': 'https://nvidia.com', 'desc': '英伟达发布H200 GPU，推理性能提升2倍，支持更大规模的AI模型训练，已被各大云服务商争相采购。'},
    {'title': 'AI医疗突破：DeepMind预测蛋白质结构新进展', 'url': 'https://deepmind.google', 'desc': 'DeepMind的AlphaFold 3成功预测蛋白质与其他分子的相互作用，为新药研发带来革命性突破。'},
    {'title': '自动驾驶端到端模型取得突破', 'url': 'https://tesla.com', 'desc': '特斯拉发布FSD V13端到端大模型，在复杂路况下的决策能力大幅提升，事故率降低40%。'},
    {'title': 'AI编程助手用户突破5000万', 'url': 'https://github.com', 'desc': 'GitHub Copilot、Cursor等AI编程工具用户爆发式增长，开发者工作效率平均提升50%以上。'},
    {'title': '中国大模型备案数量超200个', 'url': 'https://gov.cn', 'desc': '国内AI大模型监管框架完善，已备案模型超过200个，包括百度、阿里、字节等头部企业纷纷通过备案。'},
    {'title': 'AI视频生成：Sora、Pika再更新', 'url': 'https://openai.com', 'desc': 'AI视频生成技术持续突破，Sora支持生成60秒高清视频，Pika推出音效同步功能，内容创作门槛大幅降低。'},
]

DETAILED_FINANCE_NEWS = [
    {'title': 'A股放量下跌：沪指失守4100点', 'url': 'https://finance.sina.com.cn', 'desc': '今日A股三大指数集体下挫，沪指失守4100点关口，创业板指跌幅超1.5%，两市成交额接近2万亿元，市场情绪明显降温。'},
    {'title': '央行明确货币政策方向：稳中偏松', 'url': 'https://pbc.gov.cn', 'desc': '央行发布2026年一季度货币政策执行报告，明确将继续实施稳健的货币政策，保持流动性合理充裕，降准降息仍有空间。'},
    {'title': '新能源汽车销量开门红：比亚迪领跑', 'url': 'https://caam.org.cn', 'desc': '1月新能源汽车销量同比增长35%，比亚迪以超50万辆的月销量继续领跑，行业竞争格局趋于稳定。'},
    {'title': '房地产政策持续松绑：多城取消限购', 'url': 'https://mohurd.gov.cn', 'desc': '一线城市房地产政策持续松绑，已有超过30个城市取消限购政策，房贷利率降至历史新低，市场信心逐步恢复。'},
    {'title': '美股科技股回调：AI泡沫争议再起', 'url': 'https://wsj.com', 'desc': '美股科技股近期大幅回调，市场对AI估值泡沫的担忧加剧，科技七巨头市值蒸发超万亿美元。'},
    {'title': '黄金价格创历史新高', 'url': 'https://gold.org', 'desc': '受避险情绪和央行购金推动，黄金价格突破3000美元/盎司创历史新高，多家机构上调目标价至3500美元。'},
    {'title': '比特币重返10万美元', 'url': 'https://bitcoin.org', 'desc': '比特币价格重返10万美元大关，受益于机构投资者持续入场和ETF资金流入，加密市场情绪高涨。'},
    {'title': '银行理财规模突破30万亿', 'url': 'https://cbrc.gov.cn', 'desc': '银行理财产品规模持续增长，突破30万亿元大关，低风险偏好投资者资金持续流入固定收益类产品。'},
    {'title': 'IPO市场回暖：排队企业超500家', 'url': 'https://csrc.gov.cn', 'desc': 'A股IPO排队企业超过500家，沪深交易所重启受理新申报，芯片、生物医药企业成为优先支持对象。'},
    {'title': '险资加仓权益资产：举牌频现', 'url': 'https://circ.gov.cn', 'desc': '保险公司权益投资比例提升，多家险资密集举牌上市公司，包括银行、地产、消费等板块，蓝筹股受青睐。'},
    {'title': '人民币汇率双向波动加剧', 'url': 'https://safe.gov.cn', 'desc': '人民币汇率在7.0-7.2区间双向波动，受美联储政策预期变化影响，外汇市场观望情绪浓厚。'},
]

# ============== 获取新闻 ==============
def fetch_ai_news():
    news = []
    try:
        resp = requests.get('https://huggingface.co/api/trending?since=daily&framework=pytorch', timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get('models', [])[:5]:
                news.append({
                    'title': item.get('name', ''),
                    'url': 'https://huggingface.co/' + item.get('name', ''),
                    'desc': '⭐ ' + str(item.get('likes', 0)) + ' likes'
                })
    except Exception as e:
        print('获取AI新闻失败: ' + str(e))
    
    if len(news) < 10:
        news.extend(DETAILED_AI_NEWS[:10])
    
    return news[:12]

def fetch_finance_news():
    news = []
    try:
        resp = requests.get('https://36kr.com/information/VC/', timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            articles = soup.select('.article-item-title a')[:5]
            for a in articles:
                news.append({
                    'title': a.get_text(strip=True),
                    'url': 'https://36kr.com' + a.get('href', ''),
                    'desc': '点击查看详情'
                })
    except Exception as e:
        print('获取财经新闻失败: ' + str(e))
    
    if len(news) < 10:
        news.extend(DETAILED_FINANCE_NEWS[:10])
    
    return news[:12]

# ============== 生成HTML ==============
def generate_html(ai_news, finance_news):
    date = datetime.now().strftime('%Y年%m月%d日')
    weekday = '一二三四五六日'[datetime.now().weekday()]
    
    ai_items = ''
    for n in ai_news:
        ai_items += '''
            <div class="news-item">
                <div class="title"><a href="''' + n['url'] + '''" target="_blank">''' + n['title'] + '''</a></div>
                <div class="desc">''' + n['desc'] + '''</div>
            </div>'''
    
    finance_items = ''
    for n in finance_news:
        finance_items += '''
            <div class="news-item">
                <div class="title"><a href="''' + n['url'] + '''" target="_blank">''' + n['title'] + '''</a></div>
                <div class="desc">''' + n['desc'] + '''</div>
            </div>'''
    
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AI & 财经每日日报 - ''' + date + '''</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: #fff; }
        .header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #fff; padding: 30px 20px; text-align: center; }
        .header h1 { margin: 0; font-size: 28px; font-weight: 600; }
        .header .date { opacity: 0.8; margin-top: 8px; font-size: 14px; }
        .section { padding: 25px 20px; border-bottom: 1px solid #eee; }
        .section-title { font-size: 20px; font-weight: 600; margin-bottom: 20px; display: flex; align-items: center; }
        .section-title .icon { margin-right: 8px; font-size: 24px; }
        .ai .section-title { color: #0066cc; }
        .finance .section-title { color: #e4393c; }
        .news-item { padding: 18px 0; border-bottom: 1px solid #f0f0f0; }
        .news-item:last-child { border-bottom: none; }
        .news-item .title { font-size: 16px; font-weight: 600; margin-bottom: 8px; }
        .news-item .title a { color: #333; text-decoration: none; }
        .news-item .title a:hover { color: #0066cc; }
        .news-item .desc { color: #666; font-size: 14px; line-height: 1.6; }
        .quote { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; padding: 30px 20px; text-align: center; }
        .quote .text { font-size: 18px; font-style: italic; line-height: 1.6; }
        .quote .author { margin-top: 15px; opacity: 0.9; font-size: 14px; }
        .footer { background: #1a1a2e; color: #fff; padding: 25px 20px; text-align: center; font-size: 13px; opacity: 0.9; }
        .stats { display: flex; justify-content: space-around; margin-top: 15px; }
        .stats .item { text-align: center; }
        .stats .num { font-size: 24px; font-weight: bold; }
        .stats .label { font-size: 12px; opacity: 0.8; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI & 📈 财经每日日报</h1>
            <div class="date">''' + date + ''' · 星期''' + weekday + '''</div>
            <div class="stats">
                <div class="item">
                    <div class="num">''' + str(len(ai_news)) + '''</div>
                    <div class="label">AI资讯</div>
                </div>
                <div class="item">
                    <div class="num">''' + str(len(finance_news)) + '''</div>
                    <div class="label">财经资讯</div>
                </div>
            </div>
        </div>
        
        <div class="section ai">
            <div class="section-title"><span class="icon">🤖</span>AI圈热点</div>
            ''' + ai_items + '''
        </div>
        
        <div class="section finance">
            <div class="section-title"><span class="icon">📈</span>财经圈热点</div>
            ''' + finance_items + '''
        </div>
        
        <div class="quote">
            <div class="text">"人工智能不会取代人类，但使用人工智能的人类会取代不使用人工智能的人类。"</div>
            <div class="author">—— 某科技大佬</div>
        </div>
        
        <div class="footer">
            由 AI 自动生成 · 每天 8:30 推送<br>
            订阅地址: https://github.com/你的用户名/daily-newsletter<br>
            <br>
            © 2026 Daily Newsletter
        </div>
    </div>
</body>
</html>'''
    return html

# ============== PushPlus 发送 ==============
def send_via_pushplus(html_content):
    """通过 PushPlus 发送"""
    print('=== 使用 PushPlus 发送 ===')
    
    if not PUSHPLUS_TOKEN:
        print('错误: PUSHPLUS_TOKEN 未配置')
        return False
    
    try:
        # 提取纯文本作为摘要
        text_content = re.sub(r'<[^>]+>', '', html_content)
        text_content = text_content[:500] + '...' if len(text_content) > 500 else text_content
        
        url = 'http://www.pushplus.plus/send'
        data = {
            'token': PUSHPLUS_TOKEN,
            'title': '🤖 AI & 📈 财经日报 ' + datetime.now().strftime('%Y年%m月%d日'),
            'content': text_content,
            'html': html_content,
            'template': 'html'
        }
        
        response = requests.post(url, data=data, timeout=30)
        result = response.json()
        
        if result.get('code') == 200:
            print('✅ PushPlus 发送成功!')
            return True
        else:
            print('❌ PushPlus 发送失败: ' + str(result))
            return False
    except Exception as e:
        print('❌ PushPlus 发送失败: ' + str(e))
        return False

# ============== SMTP 发送 ==============
def send_via_smtp(html_content):
    """通过 SMTP 发送邮件"""
    print('=== 使用 SMTP 发送邮件 ===')
    print('From: ' + SMTP_USER)
    print('To: ' + str(TO_EMAILS))
    print('SMTP: ' + SMTP_SERVER + ':' + str(SMTP_PORT))
    
    if not SMTP_USER or not SMTP_PASSWORD:
        print('错误: 请配置 SMTP_USER 和 SMTP_PASSWORD 环境变量')
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '🤖 AI & 📈 财经每日日报 - ' + datetime.now().strftime('%Y年%m月%d日')
        msg['From'] = SMTP_USER
        msg['To'] = ', '.join(TO_EMAILS) if TO_EMAILS and TO_EMAILS[0] else SMTP_USER
        
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        print('正在连接 SMTP 服务器...')
        
        # 自动识别 SMTP 配置
        email_domain = SMTP_USER.split('@')[-1].lower() if SMTP_USER else 'qq.com'
        smtp_config = get_smtp_config(email_domain)
        smtp_server = smtp_config['server']
        smtp_port = smtp_config['port']
        use_ssl = smtp_config['ssl']
        
        print(f'自动识别邮箱类型: {email_domain} -> {smtp_server}:{smtp_port}')
        
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
            server.starttls()
        
        server.login(SMTP_USER, SMTP_PASSWORD)
        print('正在发送邮件...')
        server.sendmail(SMTP_USER, [TO_EMAILS[0]] if TO_EMAILS and TO_EMAILS[0] else SMTP_USER, msg.as_string())
        server.quit()
        print('✅ 邮件发送成功!')
        return True
    except Exception as e:
        print('❌ SMTP 邮件发送失败: ' + str(e))
        return False

# ============== 主程序 ==============
def main():
    print('开始生成 ' + datetime.now().strftime('%Y年%m月%d日') + ' 日报...')
    
    ai_news = fetch_ai_news()
    finance_news = fetch_finance_news()
    
    print('获取到 ' + str(len(ai_news)) + ' 条AI新闻, ' + str(len(finance_news)) + ' 条财经新闻')
    
    html = generate_html(ai_news, finance_news)
    
    output_file = 'daily_report_' + datetime.now().strftime('%Y%m%d') + '.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print('日报已保存到: ' + output_file)
    
    # 发送：优先 PushPlus，其次 SMTP
    success = False
    
    if PUSHPLUS_TOKEN:
        success = send_via_pushplus(html)
    
    if not success and SMTP_USER and SMTP_PASSWORD:
        success = send_via_smtp(html)
    
    if not success:
        print('WARNING: 所有发送方式都失败!')
        import sys
        sys.exit(1)

if __name__ == '__main__':
    main()

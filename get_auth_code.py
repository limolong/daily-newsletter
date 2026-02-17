#!/usr/bin/env python3
"""
QQ邮箱授权码获取助手
帮助用户获取QQ邮箱SMTP发送邮件的授权码
"""

import webbrowser
import time

def main():
    print("=" * 50)
    print("QQ邮箱授权码获取助手")
    print("=" * 50)
    
    print("""
步骤：
1. 打开QQ邮箱: https://mail.qq.com
2. 登录你的账号 (如果未登录)
3. 点击右上角「设置」
4. 选择「账户」
5. 向下滚动找到「POP3/SMTP服务」
6. 点击「开启」
7. 按照提示发送短信获取授权码
8. 复制授权码并保存

授权码示例: xxxxxxxx (16位字符串)

获取后，在当前目录创建 .env 文件，内容如下：
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
SMTP_USER=2060049165@qq.com
SMTP_PASSWORD=你的授权码
TO_EMAILS=你的收件人邮箱

然后运行: python daily_newsletter.py
""")
    
    # 自动打开QQ邮箱
    print("\n正在打开QQ邮箱...")
    webbrowser.open("https://mail.qq.com")
    print("请按回车键退出...")
    input()

if __name__ == "__main__":
    main()

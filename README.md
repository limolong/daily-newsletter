# AI & 财经每日日报

每天 8:30 自动推送 AI 圈和财经圈的最新资讯到邮箱。

## 📧 配置步骤

### 1. 克隆仓库
```bash
git clone https://github.com/你的用户名/daily-newsletter.git
cd daily-newsletter
```

### 2. 配置环境变量
创建 `.env` 文件：
```env
# 邮箱配置 (QQ邮箱)
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
SMTP_USER=your_email@qq.com
SMTP_PASSWORD=your授权码

# 收件人
TO_EMAILS=recipient1@example.com,recipient2@example.com
```

### 3. 获取QQ邮箱授权码
1. 登录 [QQ邮箱](https://mail.qq.com)
2. 设置 → 账户 → 开启 POP3/SMTP 服务
3. 获取授权码

### 4. 安装依赖
```bash
pip install -r requirements.txt
```

### 5. 运行测试
```bash
python daily_newsletter.py
```

## 🔧 GitHub Actions 自动运行

本项目已配置 GitHub Actions，每天 8:30 自动运行：

- 触发时间: 每天 08:30 UTC (16:30 北京时间)
- 无需本地运行，GitHub 自动执行

## 📁 项目结构

```
daily-newsletter/
├── daily_newsletter.py    # 主程序
├── requirements.txt       # 依赖
├── .env.example         # 环境变量模板
├── .github/
│   └── workflows/
│       └── daily.yml    # GitHub Actions 配置
└── README.md
```

## 🎨 日报样式

参考图片中的样式，包含：
- 顶部日期和标题
- AI 圈热点资讯
- 财经圈热点资讯
- 今日金句
- 底部订阅信息

## 📝 功能

- [x] 自动抓取 AI 圈热点新闻
- [x] 自动抓取财经圈热点新闻  
- [x] 生成 HTML 日报
- [x] 发送邮件到指定邮箱
- [x] GitHub Actions 定时自动运行

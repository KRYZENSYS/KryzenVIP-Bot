# 🌃 KRYZEN VIP Telegram Bot

Professional Cyberpunk-style Telegram bot with AI, Downloader, Tools, Premium subscriptions and full Admin Panel.

![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
![aiogram](https://img.shields.io/badge/aiogram-3.13-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

## ✨ Features

### 🤖 AI (10 tools)
Chat · Image Prompt · Code · Code Review · Text · Translation · Resume · Ad · SEO · Prompt Generator

### 📥 Downloader (8 platforms)
Instagram · TikTok · YouTube · Facebook · Pinterest · Threads · Spotify · Telegram

### 🛠 Tools (20+ utilities)
QR · Barcode · Hash · Password · PDF/Word · OCR · TTS/STT · URL Shortener · Calculator · Currency · Base64

### 🌐 Cyber Tools
IP · DNS · WHOIS · SSL · HTTP Headers · Ping · Port · Status · User Agent

### 💎 Monetization
- Premium subscriptions (Telegram Stars)
- Promo codes
- Referral system (5 tiers)
- Daily bonus & streak
- Spin Wheel
- Mystery Box (Premium)

### 🔐 Admin Panel
Broadcast · Stats · Ban/Unban · Premium granting · Promo creation · Logs · Backup · CSV Export

## 🚀 Quick Start

### 1. Clone & install
```bash
git clone https://github.com/KRYZENSYS/KryzenVIP-Bot.git
cd KryzenVIP-Bot
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
nano .env
```

Required:
- `BOT_TOKEN` — from @BotFather
- `ADMIN_IDS` — your Telegram ID
- `OPENAI_API_KEY` — for AI features

### 3. Run

**Local:**
```bash
python -m bot
```

**Docker:**
```bash
docker build -t kryzen-bot .
docker run -d --name kryzen --env-file .env kryzen-bot
```

**Railway.app:** Connect repo → Set env vars → Deploy

## 📁 Project Structure

```
bot/
├── __main__.py           # Entry point
├── config.py             # Pydantic settings
├── database/             # SQLAlchemy engine + models
├── handlers/             # Telegram handlers (12 modules)
├── keyboards/            # Inline + Reply keyboards
├── middlewares/          # DB, throttling, auth, ban
├── services/             # AI, Downloader, Payment, Achievements
├── states/               # FSM states
└── utils/                # Helpers, decorators, levels
```

## 📜 License

MIT License — free for personal & commercial use.

Made with 💜 by [KRYZENSYS](https://github.com/KRYZENSYS)
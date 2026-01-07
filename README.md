# Fengshui Warning Bot

A Telegram bot delivering daily Feng Shui guidance based on Vietnamese lunar calendar data.

**Version:** 1.0 | **Status:** Stable | **Author:** @phulengo

## Features

- **Daily Feng Shui Readings** - Get comprehensive daily guidance via `/today` command
- **Scheduled Warnings** - Bot broadcasts age warnings + inauspicious stars daily at 07:00
- **Complete Data** - Solar/lunar dates, auspicious/inauspicious hours, five elements, lucky stars, travel directions
- **Beautiful Formatting** - Telegram MarkdownV2 with emoji indicators for visual clarity
- **Health Check** - Container-ready endpoint for orchestration platforms

## Quick Start

### Prerequisites

- Python 3.7+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Chat ID (your personal chat or group)

### Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd fengshui-telegram-bot
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your TELEGRAM_TOKEN and CHAT_ID
```

5. Run the bot:
```bash
python bot.py
```

Bot is ready when you see: `Application started, awaiting updates...`

## Usage

### Commands

**`/start`** - Welcome message
```
Hello! I'm your Feng Shui Bot. Use /today to get today's Feng Shui info.
```

**`/today`** - Daily Feng Shui reading
Returns comprehensive reading including:
- Solar & lunar dates
- Good/bad hours (giờ tốt/giờ xấu) with time ranges
- Five elements (Ngũ Hành) for year, day, season
- Daily star name & zodiac animal
- Auspicious (🔴) & inauspicious (⚫️) stars with explanations
- Zodiac age warnings (tuổi kỵ)
- Lucky travel directions (Hỷ thần, Tài thần)

Example output:
```
📅 Thứ tư, Ngày 17 Tháng 9 Năm 2025

🌙 ÂM LỊCH:
Ngày 26 Tháng 7 Năm 2025
└ Ngày Kỷ Sửu, tháng Giáp Thân, năm ất Tỵ

🕑 GIỜ TỐT:
🔴 Bính Dần
    └ (3h-5h)
...
```

### Scheduled Daily Warning

Bot automatically sends warnings at 07:00 (Asia/Bangkok timezone) daily:
```
⚠️ Cảnh báo ngày 17 Tháng 9 Năm 2025
🚫 Tuổi kỵ: Đinh Mùi, Ất Mùi
🔹 Lý do: Có các sao hung: Thụ Tử, Ngũ Quỷ
```

## Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Required
TELEGRAM_TOKEN=<your-bot-token-from-@botfather>
CHAT_ID=<your-chat-id-or-group-id>

# Optional
PORT=8443  # Health check server port (default: 8443)
```

**Getting Chat ID:**
1. Send any message to your bot
2. Visit: `https://api.telegram.org/bot<TELEGRAM_TOKEN>/getUpdates`
3. Find your chat ID in the JSON response (under `message.chat.id`)

### Timezone

Bot uses **Asia/Bangkok (UTC+7)** by default. To change:

Edit `bot.py`:
```python
# Find this line:
today_str = datetime.now(pytz.timezone("Asia/Bangkok")).strftime("%Y-%m-%d")

# Replace "Asia/Bangkok" with your timezone, e.g.:
# datetime.now(pytz.timezone("America/New_York"))
```

Available timezones: [pytz timezone list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

## Deployment

### Docker

1. Build image:
```bash
docker build -t fengshui-bot .
```

2. Run container:
```bash
docker run -e TELEGRAM_TOKEN=<token> -e CHAT_ID=<id> \
           -p 8443:8443 \
           fengshui-bot
```

3. Health check:
```bash
curl http://localhost:8443/health
# Expected: {"status":"ok"}
```

### Cloud Platforms

Bot supports cloud deployment via health endpoint:

**Render/Railway/Heroku:**
- Health Check: `GET /health` (port 8443)
- Ready to scale: Stateless design (all data immutable)

## Architecture

**Components:**
- **bot.py** (304 LOC) - Telegram bot, command handlers, daily job
- **scraping.py** (428 LOC) - Web scraper for calendar data
- **lich_van_nien_thoigian_2025.json** - Pre-scraped calendar cache (Sep 2025 - Jan 2026)

**Data Flow:**
```
Vietnamese Calendar Sources
    ↓ (scraping.py)
JSON Cache
    ↓ (bot.py loads at startup)
In-Memory Store
    ↓ (user command /today or daily job)
Format + MarkdownV2 Escape
    ↓
Telegram API
    ↓
User/Group Chat
```

See [System Architecture](./docs/system-architecture.md) for detailed design documentation.

## Documentation

- [**Project Overview & PDR**](./docs/project-overview-pdr.md) - Requirements, acceptance criteria, roadmap
- [**Codebase Summary**](./docs/codebase-summary.md) - File structure, components, data format
- [**Code Standards**](./docs/code-standards.md) - Naming conventions, formatting, best practices
- [**System Architecture**](./docs/system-architecture.md) - Design patterns, data flow, scaling

## Data Coverage

**Calendar Data:** September 2025 - January 2026

To extend coverage, regenerate calendar data:
```bash
python scraping.py
```

Modify dates in scraping.py:
```python
start_date = datetime(2025, 9, 17)  # Change start date
end_date = datetime(2026, 1, 31)    # Change end date
```

## Troubleshooting

**Bot doesn't respond to commands:**
- Check TELEGRAM_TOKEN and CHAT_ID in .env
- Verify bot is running: `python bot.py`
- Check network connectivity

**Daily warning doesn't send:**
- Verify CHAT_ID is correct
- Check timezone setting matches deployment environment
- Confirm bot is running continuously (use process manager: supervisord, systemd)

**MarkdownV2 formatting errors:**
- Bot includes special character escaping; usually transparent
- If issues persist, check Telegram API docs for reserved characters

**Calendar data not found for today:**
- Today's date not in lich_van_nien_thoigian_2025.json
- Regenerate calendar data via scraping.py

**Health check failing:**
- Verify PORT environment variable (default: 8443)
- Check no firewall blocking the port
- Confirm Flask server started (check logs)

## Development

### Project Structure
```
.
├── bot.py                           # Main bot application
├── scraping.py                      # Data ingestion script
├── requirements.txt                 # Dependencies
├── .env                            # Configuration (not committed)
├── README.md                       # This file
└── docs/                          # Project documentation
    ├── project-overview-pdr.md
    ├── codebase-summary.md
    ├── code-standards.md
    └── system-architecture.md
```

### Adding Features

1. Add new command handler in bot.py:
```python
async def mycommand(update, context):
    await update.message.reply_text("Response")

application.add_handler(CommandHandler("mycommand", mycommand))
```

2. Regenerate calendar data if needed:
```bash
python scraping.py
```

3. Test locally:
```bash
python bot.py
```

### Testing

Send test messages to bot on Telegram:
- `/start` - Should respond with welcome
- `/today` - Should show complete daily reading
- Invalid command - Should be ignored gracefully

## Performance

| Metric | Value |
|--------|-------|
| Bot Startup | ~2 seconds |
| /today Response | ~0.5 seconds |
| Daily Warning Send | ~0.5 seconds |
| Memory Usage | ~100MB |
| Calendar Data | ~50MB (in-memory) |

## Security

- **Secrets:** TELEGRAM_TOKEN and CHAT_ID stored in .env (not committed)
- **No Logging:** Bot doesn't log sensitive data
- **No Persistence:** Messages processed, not stored
- **API Safety:** python-telegram-bot handles rate limiting

## Known Limitations

- Vietnamese language only
- Calendar data limited to Sep 2025 - Jan 2026 (regenerate via scraping.py)
- Single bot instance (no clustering in v1.0)
- No user preferences or customization
- No command history

## Roadmap (v1.1+)

- Multi-language support (English, Chinese)
- User preference storage (timezone, alert time)
- `/history` command (past readings)
- Star explanations and recommendations
- Admin dashboard for metrics

## License

© 2025 Fengshui Warning Bot - @phulengo

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review [Code Standards](./docs/code-standards.md) for implementation details
3. Contact author: @phulengo

---

**Last Updated:** 2025-01-07 | **Version:** 1.0

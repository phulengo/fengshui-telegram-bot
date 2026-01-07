# Codebase Summary

**Project:** Fengshui Warning Telegram Bot
**Version:** 1.0
**Language:** Python 3
**Total LOC:** ~732 (application code)
**Last Updated:** 2025-01-07

## Overview

A Telegram bot delivering daily Feng Shui insights based on Vietnamese lunar calendar data. Provides auspicious/inauspicious hours, five elements, lucky directions, and zodiac age warnings.

## Core Architecture

### File Structure

```
.
├── bot.py                          (304 LOC) - Main Telegram bot application
├── scraping.py                     (428 LOC) - Calendar data web scraper
├── requirements.txt                (7 deps)  - Python dependencies
├── lich_van_nien_thoigian_2025.json (large)  - Pre-scraped 2025 calendar data
├── data_demo_template.json         (sample)  - Data structure template
└── .env                            - Config (TELEGRAM_TOKEN, CHAT_ID)
```

### Application Components

#### 1. **bot.py** - Main Telegram Bot (304 LOC)

**Responsibilities:**
- Flask health check server (port 8443)
- Telegram bot command handlers
- Daily scheduled warnings
- MarkdownV2 text formatting

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `escape_markdown_v2()` | Escapes special chars for Telegram MarkdownV2 |
| `pretty_star_list()` | Formats auspicious/inauspicious stars with icons |
| `format_time_fancy()` | Formats good/bad hours (giờ tốt/giờ xấu) |
| `format_season_element()` | Formats seasonal five elements (Ngũ Hành) |
| `safe_bold()` | Smart bolding (skips if escapes present) |

**Commands:**
- `/start` - Welcome message
- `/today` - Get comprehensive daily Feng Shui reading

**Scheduled Job:**
- `daily_warning()` - Runs 07:00 (Asia/Bangkok) daily, broadcasts to CHAT_ID

**Key Constants:**
```python
BOT_VERSION = "1.0"
BOT_AUTHOR = "@phulengo"
```

**Data Processing:**
Loads JSON at startup → formats with strict MarkdownV2 escaping → sends via Telegram API

#### 2. **scraping.py** - Web Scraper (428 LOC)

**Responsibilities:**
- Fetches calendar data from 3 Vietnamese sources
- Normalizes text (PascalCase conversion, Vietnamese term mappings)
- Builds JSON structure for daily records

**Data Sources:**
| Source | Data Type |
|--------|-----------|
| thoigian.com.vn | Calendar dates, times, elements |
| licham.vn | Star names |
| baomoi.com | Five elements |

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `get_day_data()` | Main scraper orchestrator |
| `to_pascal_case()` | Normalize Vietnamese text to PascalCase |
| `replace_exact_words()` | Vietnamese term mapping (e.g., "Tháng Một" → "Tháng 1") |

**Scraping Range:** September 2025 - January 2026

**Mappings:**
- 12 two-hour periods (Tí, Sửu, Dần, Mão, etc.) with time ranges
- Good/bad stars with red (🔴) / black (⚫️) indicators
- Five elements with colors (🔴 Hoả, 🟢 Mộc, 🔵 Thủy, 🟡 Kim, 🟤 Thổ)

#### 3. **Data Structure** - lich_van_nien_thoigian_2025.json

**Schema per date (YYYY-MM-DD):**

```json
{
  "date": "Solar date string",
  "lunar-date": "Lunar date",
  "detail-lunar-date": "Heavenly Stem & Branch",
  "good-time": ["Array of auspicious hours"],
  "bad-time": ["Array of inauspicious hours"],
  "year-element": "5-element for year",
  "date-element": "5-element for day",
  "season-element": {
    "Season": {
      "Tiết khí": "Solar term",
      "Vượng": "Thriving element",
      "Khắc": "Suppressed element"
    }
  },
  "star": "Daily star name",
  "animal": "Daily zodiac animal",
  "bad-for-age": ["Ages to avoid"],
  "division": {"Trực name": "Description"},
  "auspicious-star": [{"Star 🔴": {"🍀": "status", "🧿": "note"}}],
  "inauspicious-star": [{"Star ⚫️": {"⚠️": "status", "🧿": "note"}}],
  "depart": {"Hỷ thần": "Direction", "Tài thần": "Direction"}
}
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| python-telegram-bot | Latest | Telegram API wrapper |
| python-telegram-bot[job-queue] | Latest | Scheduled job support |
| flask | Latest | Health check endpoint |
| requests | Latest | HTTP requests for scraping |
| beautifulsoup4 | Latest | HTML parsing |
| lxml | Latest | XML/HTML parser |
| pytz | Latest | Timezone (Asia/Bangkok UTC+7) |
| python-dotenv | Latest | Environment variable loading |

## Configuration

**Environment Variables (.env):**
```
TELEGRAM_TOKEN=<bot-token-from-@botfather>
CHAT_ID=<target-chat-id>
PORT=8443  # Optional, health server port
```

## Data Flow

```
Vietnamese Calendar Sources
        ↓
    scraping.py (fetch & normalize)
        ↓
lich_van_nien_thoigian_2025.json (cache)
        ↓
    bot.py (load at startup)
        ↓
    User Commands (/today) or Scheduled (07:00 daily)
        ↓
Format & MarkdownV2 Escape
        ↓
Telegram API → User/Chat
```

## Deployment Pattern

- **Runtime:** Python 3.x polling mode
- **Health Check:** GET `/health` → `{"status": "ok"}`
- **Container Ready:** Health endpoint enables Docker/cloud deployment
- **Timezone:** Asia/Bangkok (UTC+7)

## Code Standards

- No type hints
- Regex-heavy text processing
- Emoji-based status indicators (🔴 good, ⚫️ bad)
- Vietnamese language strings throughout
- No unit tests present
- Single-threaded bot + daemon health server

## Key Design Patterns

1. **Pre-scraped Data:** Avoids repeated scraping; loads JSON at startup
2. **Strict Markdown Escaping:** Custom escape logic for Telegram's MarkdownV2
3. **Exception Mapping:** Star names mapped to special emojis (🧧 🚨) based on lists
4. **Text Formatting:** Hierarchical format functions (escape → bold → time → season)

## Maintenance Notes

- **Calendar Updates:** Regenerate `lich_van_nien_thoigian_2025.json` via `scraping.py` for new dates
- **Star Mappings:** Adjust `exception_good` / `exception_bad` sets in `bot.py` as needed
- **Timezone:** Currently hardcoded to Asia/Bangkok; modify if deployment region changes
- **Health Endpoint:** Required for container orchestration; do not remove

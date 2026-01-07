# Code Standards & Codebase Structure

**Project:** Fengshui Warning Bot
**Version:** 1.0
**Last Updated:** 2025-01-07

## Codebase Organization

### Directory Layout

```
.
├── bot.py                              Main application entry point
├── scraping.py                         Web scraper utilities
├── requirements.txt                    Python dependencies
├── lich_van_nien_thoigian_2025.json   Pre-scraped calendar data cache
├── data_demo_template.json            Sample JSON structure
├── .env                               Runtime configuration (not committed)
├── .gitignore                         Git ignore rules
├── README.md                          User documentation
├── docs/                              Project documentation
│   ├── project-overview-pdr.md       High-level requirements
│   ├── codebase-summary.md           Code architecture overview
│   ├── code-standards.md             This file
│   ├── system-architecture.md        System design
│   └── deployment-guide.md           Setup & deployment
└── plans/                             Developer planning (CI/CD, reports)
```

### Module Responsibilities

| Module | Purpose | LOC |
|--------|---------|-----|
| `bot.py` | Telegram bot logic, Flask server, message formatting | 304 |
| `scraping.py` | Web scraping, text normalization, data transformation | 428 |

## Code Standards

### Python Style

**Language Version:** Python 3.x
**Style Guide:** PEP 8 (unofficial)
**Type Hints:** Not used (Python 3.6 compatibility)
**Async:** Used for Telegram bot handlers (python-telegram-bot async API)

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Variables | snake_case | `fengshui_data`, `divider_line` |
| Functions | snake_case | `escape_markdown_v2()`, `format_time_fancy()` |
| Constants | UPPER_CASE | `BOT_VERSION`, `TELEGRAM_TOKEN` |
| Classes | PascalCase | Application, CommandHandler |
| Private | _leading_underscore | `_helper()` (not used in current codebase) |

### Code Structure: bot.py

**Sections in order:**

```python
1. Imports (standard library, third-party)
2. Flask app initialization + health endpoint
3. Constants (BOT_VERSION, BOT_AUTHOR, BOT_COPYRIGHT)
4. Utility functions (escape, format, clean)
5. Bot command handlers (async def start, today)
6. Scheduled job handler (async def daily_warning)
7. Main entry point (def main())
8. Script execution guard (if __name__ == "__main__")
```

**Key Functions:**

```python
# Text Processing (escape.py equivalent)
escape_markdown_v2(text)           # Escapes all MarkdownV2 special chars
contains_escape(text)              # Detects existing escapes
safe_bold(text)                    # Bolds only if safe (no existing escapes)
esc(x)                            # Shorthand for escape_markdown_v2()

# Message Formatting
pretty_star_list(star_list)        # Formats auspicious/inauspicious stars
format_time_fancy(times)           # Formats good/bad hours
format_season_element(season_dict) # Formats five elements by season
move_dot_first(element)            # Reorders emoji indicators to front

# Bot Handlers
start(update, context)             # /start command
today(update, context)             # /today command
daily_warning(context)             # 07:00 daily job

# Infrastructure
start_health_server()              # Daemon Flask server
main()                             # Application entry point
```

### Code Structure: scraping.py

**Sections in order:**

```python
1. Imports (requests, BeautifulSoup, etc.)
2. Text utilities (to_pascal_case, replace_exact_words)
3. Replacement dictionaries (month names, zodiac hours, star mappings)
4. Web scraping functions
5. Data transformation and output
```

**Text Processing Pipeline:**

```
Raw HTML from websites
    ↓
BeautifulSoup parse + CSS selectors
    ↓
to_pascal_case() → normalize capitalization
    ↓
replace_exact_words() → apply mapping dictionary
    ↓
Structured JSON output
```

## Formatting Standards

### String Formatting

**MarkdownV2 Escaping:**
```python
# Character escape list for Telegram MarkdownV2
escape_chars = r"_*\[\]()~`>#+-=|{}.!"
```

**Emoji Indicators:**
- 🔴 Red circle = Good/auspicious
- ⚫️ Black circle = Bad/inauspicious
- 🧧 Red envelope = Special good star
- 🚨 Alarm = Special bad star
- 🌱 🌞 🍂 ❄️ = Seasons (spring, summer, autumn, winter)

**Message Structure:**

```
📅 Header (date)
─────────────────
Section 1
Section 2
─────────────────
Final info
─────────────────
© Copyright line
```

### Comments & Documentation

**Function Documentation:**
```python
def function_name(param1, param2):
    """One-line purpose statement.

    Longer description if complex.
    """
    # Inline comment for non-obvious logic
    pass
```

**Inline Comments:**
- Used sparingly for complex regex or nested conditions
- Explain "why", not "what" (code should be self-explanatory)

**No Comments:** Current codebase minimal; add for future maintenance

### Error Handling

**Current Pattern:**
```python
# Graceful degradation for missing data
data = fengshui_data.get(today_str)
if not data:
    await update.message.reply_text("No data found for today.")
    return
```

**Best Practices for New Code:**
- Catch exceptions explicitly (not bare `except:`)
- Log errors before recovery attempts
- Return meaningful error messages to user
- Don't silently fail; always inform user of missing data

## Data Structures

### Calendar JSON Schema

**File:** `lich_van_nien_thoigian_2025.json`
**Format:** JSON object keyed by date (YYYY-MM-DD)

```json
{
  "2025-09-17": {
    "date": "Thứ tư, Ngày 17 Tháng 9 Năm 2025",
    "lunar-date": "Ngày 26 Tháng 7 Năm 2025",
    "detail-lunar-date": "Ngày Kỷ Sửu, tháng Giáp Thân, năm ất Tỵ",
    "all-time": ["Array of 12 two-hour periods"],
    "good-time": ["Bính Dần (3h-5h)", "Đinh Mão (5h-7h)", ...],
    "bad-time": ["Opposite of good-time"],
    "year-element": "Hoả 🔴 - Phú Đăng Hoả",
    "date-element": "Hoả 🔴 - Bích Lôi Hoả",
    "season-element": {
      "Mùa Thu": {
        "Tiết khí": "Thu phân (giữa thu)",
        "Vượng": "Kim",
        "Khắc": "Hoả Trọng"
      }
    },
    "star": "Chẩn",
    "animal": "Giun",
    "bad-for-age": ["Đinh Mùi", "Ất Mùi"],
    "division": {"Khai": "Tốt mọi việc, trừ động thổ, an táng"},
    "auspicious-star": [
      {"Mẫu Thương 🔴": {"🍀": "good", "🧿": "note"}}
    ],
    "inauspicious-star": [
      {"Thụ Tử ⚫️": {"⚠️": "warning", "🧿": "note"}}
    ],
    "depart": {
      "Hỷ thần": "Đông Bắc",
      "Tài thần": "Nam"
    }
  }
}
```

**Field Definitions:**

| Field | Type | Description |
|-------|------|-------------|
| date | string | Formatted solar date |
| lunar-date | string | Lunar date |
| detail-lunar-date | string | Heavenly stem & branch |
| good-time | array | Auspicious 2-hour periods |
| bad-time | array | Inauspicious 2-hour periods |
| year-element | string | Year's five element + icon |
| date-element | string | Day's five element + icon |
| season-element | object | Seasonal info (term, thriving, suppressed) |
| star | string | Daily star name |
| animal | string | Zodiac animal |
| bad-for-age | array | Ages to avoid (e.g., "Đinh Mùi") |
| division | object | "Trực" name and description |
| auspicious-star | array | Good stars with status/notes |
| inauspicious-star | array | Bad stars with status/notes |
| depart | object | Travel directions (Hỷ thần, Tài thần) |

### Environment Variables

**File:** `.env` (not committed)
**Example:**
```env
TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
CHAT_ID=-1001234567890
PORT=8443
```

## Configuration Management

**Approach:** Environment-based (12-factor app methodology)

**Constants in Code:**
```python
BOT_VERSION = "1.0"
BOT_AUTHOR = "@phulengo"
BOT_COPYRIGHT = f"© 2025 Fengshui Warning Bot • v{BOT_VERSION} • by {BOT_AUTHOR}"

# Special star mappings (hardcoded, but easily editable)
exception_good = {"Thiên tài", "Địa tài", "Trực tinh", ...}
exception_bad = {"Địa tặc", "Sát chủ", "Ngũ quỷ", ...}
```

**Configurable Without Code Changes:**
- Emoji icon mappings (in `pretty_star_list()`)
- Star exception lists (at bot.py top)
- Scheduled job time (currently 07:00; in `main()`)
- Timezone (currently Asia/Bangkok; in `today()`)

## Testing Strategy

**Current State:** No unit tests
**Recommended Additions (Future):**
- Test `escape_markdown_v2()` with special char combinations
- Test `format_time_fancy()` with edge cases
- Mock Telegram API for command handlers
- Validate JSON schema on data load
- Test MarkdownV2 output renders without errors

## Performance Considerations

| Operation | Complexity | Impact |
|-----------|-----------|--------|
| Bot startup | O(1) | Load JSON once (~1s) |
| /today command | O(1) | Lookup date, format (~0.5s) |
| Daily warning | O(1) | Same as /today (~0.5s) |
| Escape function | O(n) | Per character; negligible for messages |
| Health check | O(1) | Instant Flask response |

**Memory Usage:**
- JSON cache: ~50MB (typical calendar data)
- Bot runtime: ~20-30MB
- Total footprint: ~100MB ✓

## Security Guidelines

1. **Never commit .env:** Use .gitignore to exclude
2. **No logging secrets:** Bot tokens, chat IDs not logged
3. **Input validation:** Check date exists in JSON before processing
4. **API safety:** python-telegram-bot handles rate limiting
5. **No data retention:** Messages processed, not stored

## Dependency Management

**File:** `requirements.txt`
**Update Strategy:**
- Pin versions for production stability
- Test updates in dev before production
- Run `pip install -r requirements.txt` on deployment

**Current Dependencies:**
- python-telegram-bot[job-queue] - Async bot + scheduling
- flask - Health check server
- requests, beautifulsoup4, lxml - Web scraping
- pytz - Timezone handling
- python-dotenv - Env var loading

## Maintenance Checklist

### Weekly
- [ ] Monitor bot health endpoint
- [ ] Verify daily warning sends at 07:00
- [ ] Check for missed /today responses

### Monthly
- [ ] Review dependency updates
- [ ] Spot-check calendar data accuracy
- [ ] Analyze error logs (if any)

### Quarterly
- [ ] Extend calendar data (re-run scraper)
- [ ] Review star exception mappings
- [ ] Update documentation if code changes

### Annually
- [ ] Full security audit
- [ ] Performance profiling
- [ ] User feedback collection
- [ ] Plan next version features

## Refactoring Opportunities (Future)

1. **Extract Formatting:** Move format functions to separate module
2. **Add Type Hints:** Python 3.9+ type annotations for maintainability
3. **Configuration Module:** Centralize all constants/config
4. **Database Layer:** Optional SQLite for user preferences
5. **Logging:** Structured logging (JSON format) for monitoring
6. **Tests:** Unit and integration test suite
7. **Async Scraper:** Non-blocking data refresh in background
8. **i18n Layer:** Support multiple languages

## References

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot Documentation](https://python-telegram-bot.readthedocs.io/)
- [MarkdownV2 Guide](https://core.telegram.org/bots/formatting#markdownv2-style)
- [PEP 8 Style Guide](https://pep8.org/)
- [Vietnamese Lunar Calendar](https://thoigian.com.vn/)

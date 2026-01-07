# System Architecture

**Project:** Fengshui Warning Bot
**Version:** 1.0
**Last Updated:** 2025-01-07

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Users/Groups                     │
└────────────────────────┬──────────────────────────────────────┘
                         │ Telegram Bot API (HTTPS)
                         ↓
        ┌────────────────────────────────┐
        │   Telegram Bot (Polling Mode)   │
        │  - Async message handlers      │
        │  - /start, /today commands     │
        │  - Job queue (07:00 daily)     │
        └────────────────────────────────┘
                         │
        ┌────────────────┴─────────────────┐
        ↓                                  ↓
    ┌────────────────┐          ┌──────────────────┐
    │  bot.py        │          │  Flask Health    │
    │ (Telegram Bot) │          │  Server :8443    │
    └────────────────┘          └──────────────────┘
        │                              │
        │ Loads at startup             │ GET /health
        ↓                              ↓
┌──────────────────────────────────────────────────┐
│  lich_van_nien_thoigian_2025.json (In-Memory)    │
│  Calendar Cache (49.5K+ lines, ~50MB)           │
└──────────────────────────────────────────────────┘
        │
        └─── Data flows to messages
            (format, escape, send via Telegram)
```

## Component Breakdown

### 1. Telegram Bot Core (bot.py)

**Technology:** python-telegram-bot library (async)
**Runtime:** Long-running polling process
**Concurrency:** Handles multiple user requests concurrently via asyncio

```
┌─────────────────────────────────────────────────┐
│         Telegram Bot Application                 │
│                                                  │
│  Handlers:                                      │
│  ├─ CommandHandler(/start)                      │
│  ├─ CommandHandler(/today)                      │
│  └─ JobQueue (daily_warning @ 07:00)            │
│                                                  │
│  User Request Flow:                             │
│  ├─ Fetch date from calendar JSON              │
│  ├─ Format with formatting functions           │
│  ├─ Escape MarkdownV2 special characters       │
│  └─ Send via Telegram API                      │
└─────────────────────────────────────────────────┘
```

**Async Handlers:**
```python
async def start(update, context)
    # Responds to /start command
    # Returns: Welcome message

async def today(update, context)
    # Responds to /today command
    # Fetches: fengshui_data[today_date]
    # Returns: Formatted daily reading

async def daily_warning(context)
    # Scheduled job (07:00 daily)
    # Sends: Age warnings + inauspicious stars
    # Target: CHAT_ID (broadcast)
```

**Message Formatting Pipeline:**

```
Raw Data (from JSON)
    ↓
clean_all(value)  → Convert list/dict to string
    ↓
format_season_element()  → Add season icons 🌱🌞🍂❄️
format_time_fancy()      → Format hours with icons 🔴⚫️
pretty_star_list()       → Map stars to emoji exceptions
move_dot_first()         → Reorder emoji to front
    ↓
escape_markdown_v2()  → Escape all special chars
escape_leading_dash_per_line()  → Escape dashes
    ↓
safe_bold()  → Apply bold formatting (if safe)
    ↓
Final Message (ready for Telegram)
```

### 2. Health Check Server (Flask)

**Purpose:** Container orchestration, liveness probe
**Endpoint:** GET http://localhost:8443/health
**Response:**
```json
{"status": "ok"}
```

**Why Separate Thread:**
- Bot polling runs main thread (long-lived)
- Health server in daemon thread (responsive)
- Allows container to verify bot is alive without bot interaction

```python
@app.route("/health")
def health():
    return {"status": "ok"}, 200

def start_health_server():
    port = int(os.environ.get("PORT", "8443"))
    app.run(host="0.0.0.0", port=port, use_reloader=False, debug=False)

# In main():
threading.Thread(target=start_health_server, daemon=True).start()
application.run_polling()  # Main thread
```

### 3. Data Layer (JSON Cache)

**File:** `lich_van_nien_thoigian_2025.json`
**Format:** JSON object, keys are dates (YYYY-MM-DD)
**Load Strategy:** Entire file loaded into memory at bot startup
**Access Pattern:** O(1) dictionary lookup by date

**Advantages:**
- Fast startup (no DB init)
- Zero network calls after startup
- Simple to update (regenerate JSON file)
- Human-readable for debugging

**Limitations:**
- Limited to pre-scraped date range (Sep 2025 - Jan 2026)
- All data in memory (scales to ~100MB for multi-year data)
- No incremental updates; full reload required

### 4. Data Ingestion (scraping.py)

**Triggered By:** Manual execution (not automated in v1.0)
**Sources:** 3 Vietnamese calendar websites

```
thoigian.com.vn  ──┐
                    │─── Scrape & Normalize ──→ JSON Output
licham.vn ────────┤
                    │
baomoi.com ───────┘
```

**Text Processing:**
```python
to_pascal_case(text)  → "tháng Một" → "Tháng Một"
replace_exact_words(text, dict)  → Apply mapping dictionary
```

**Mapping Example:**
```python
replacements = {
    "Tháng Một": "Tháng 1",      # Month name normalization
    "Tí": "Tí (0:00 - 1:00 & 23:00 - 0:00)",  # Zodiac hour + time range
    "Kim quỹ": "Kim quỹ - 🔴",    # Star + icon mapping
}
```

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│  Startup Phase                                            │
│                                                            │
│  1. Load .env (TELEGRAM_TOKEN, CHAT_ID)                  │
│  2. Load lich_van_nien_thoigian_2025.json into memory    │
│  3. Initialize Telegram Application with token           │
│  4. Register handlers (/start, /today)                   │
│  5. Register daily job (07:00 Asia/Bangkok)              │
│  6. Start Flask health server (daemon thread)            │
│  7. Start bot polling (main thread)                      │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  User Command: /start                                     │
│                                                            │
│  1. Telegram sends update to bot                         │
│  2. start() handler triggered                            │
│  3. Reply: Welcome message                               │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  User Command: /today                                     │
│                                                            │
│  1. Get current date: datetime.now(Asia/Bangkok)        │
│  2. Lookup date in JSON: fengshui_data[YYYY-MM-DD]      │
│  3. Format each field:                                   │
│     ├─ dates → solar/lunar string                        │
│     ├─ times → emoji + time range                        │
│     ├─ elements → color indicator + name                │
│     ├─ stars → map to 🧧 or 🚨 if in exception list     │
│     └─ directions → add 🧭 icon                         │
│  4. Join all sections with dividers                      │
│  5. Escape MarkdownV2 special characters                 │
│  6. Apply bold formatting (safely)                       │
│  7. Send via Telegram API with parse_mode="MarkdownV2"  │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  Daily Job: 07:00 (Asia/Bangkok Timezone)                │
│                                                            │
│  1. Job queue triggers daily_warning()                   │
│  2. Same date lookup + formatting as /today              │
│  3. Extract only: bad-for-age + inauspicious-star        │
│  4. Create warning message                               │
│  5. Send to CHAT_ID via Telegram API                     │
│  6. Next execution: Tomorrow 07:00                        │
└──────────────────────────────────────────────────────────┘
```

## Timezone & Scheduling

**Primary Timezone:** Asia/Bangkok (UTC+7)
**All Times:** Referenced as Asia/Bangkok unless specified

```python
import pytz
today_str = datetime.now(pytz.timezone("Asia/Bangkok")).strftime("%Y-%m-%d")

# Job queue uses UTC internally, but time specified in local context
job_queue.run_daily(
    daily_warning,
    time=datetime.strptime("07:00", "%H:%M").time(),  # 07:00 local
    days=(0, 1, 2, 3, 4, 5, 6)  # Every day
)
```

**Considerations for Deployment:**
- If moving to different timezone, update pytz.timezone() call
- Verify container/server timezone matches deployment region
- Health check endpoint has no timezone dependency

## Message Format Structure

**MarkdownV2 Format Requirements:**

```
Special characters that need escaping:
_ * \ [ ] ( ) ~ ` > # + - = | { } . !

Emoji Indicators:
🔴 Red circle     = Good/auspicious hours/stars
⚫️ Black circle   = Bad/inauspicious hours/stars
🧧 Red envelope   = Special good star (exception)
🚨 Alarm          = Special bad star (exception)

Section Markers:
─────────────────  = Visual divider
📅 📅 Calendar icon
🌙 Moon (lunar)
🕑 Clock (time)
☯️ Yin-yang (elements)
🌟 Star
🚫 Prohibition (ages)
🐾 Animal paw
🧿 Evil eye (general)
🧭 Compass (directions)
🧧 Red envelope (prosperity)
💰 Money (wealth)
```

**Example Message Section:**
```
*GIỜ TỐT:*
🔴 Bính Dần
    └ (3h-5h)
🔴 Đinh Mão
    └ (5h-7h)
```

## Scalability & Deployment Model

### Current Deployment
- **Environment:** Single instance (bot + Flask health server)
- **Concurrency:** python-telegram-bot handles multiple user requests
- **Scaling:** Suitable for ~100+ concurrent users per bot instance
- **State:** Shared (calendar JSON in memory)

### Horizontal Scaling (Future)
To run multiple bot instances:
1. Each instance loads calendar JSON (immutable, no sync needed)
2. Telegram API routes requests to available instances
3. Daily job runs on all instances (sends duplicate warnings; mitigate with job locking)
4. Health check enables load balancer integration

### Vertical Scaling
- Increase memory for larger date ranges in JSON
- Optimize escaping function (regex compilation)
- Add database layer for performance queries

## Error Handling Strategy

```
Scenario 1: Missing date in calendar
├─ Check: data = fengshui_data.get(today_str)
├─ Condition: if not data
└─ Action: Reply "No data found for today."

Scenario 2: Invalid environment variables
├─ Check: os.getenv("TELEGRAM_TOKEN") returns None
├─ Condition: if not TOKEN
└─ Action: Application.builder() fails gracefully

Scenario 3: Telegram API rate limit
├─ python-telegram-bot handles internally
└─ Auto-retry with backoff (transparent to bot)

Scenario 4: Network timeout during command
├─ Telegram API timeout
└─ User sees "request timeout" error (Telegram client)
```

## Security Model

**Data at Rest:**
- Calendar JSON: Plain text (no sensitive data)
- .env: Local filesystem, not committed to git
- No logs containing secrets

**Data in Transit:**
- Telegram API: HTTPS/TLS encrypted
- Flask health endpoint: Same server (local)
- Bot polling: TLS to Telegram servers

**Access Control:**
- Bot: Single token from environment
- Chat ID: Hardcoded in environment, never user input
- No user authentication (broadcast model)

## Monitoring & Observability

**Health Check:**
```bash
curl http://localhost:8443/health
# Expected: {"status": "ok"} 200 OK
```

**Logs (Recommended Future):**
- Bot startup: "Application started, awaiting messages"
- Command handler: "Received /today from user_id, responded in Xms"
- Daily job: "Broadcast warning to CHAT_ID at 07:00"
- Errors: "Exception in handler, retrying..."

**Metrics (Recommended Future):**
- Commands per day (/start, /today)
- Daily job success rate
- Message delivery rate
- Response time percentiles (p50, p95, p99)
- Calendar coverage dates

## Disaster Recovery

**Data Loss Scenarios:**

| Scenario | Impact | Recovery |
|----------|--------|----------|
| lich_van_nien_thoigian_2025.json deleted | Bot replies "No data for today" | Regenerate via scraping.py |
| .env deleted | Bot fails to authenticate | Restore from backup / regenerate |
| Bot process crashes | Users get no response | Auto-restart (container restarts) |
| Telegram service down | All messaging fails | Wait for Telegram (external) |

**Backup Strategy (Recommended):**
- Store calendar JSON in version control (immutable by date)
- Store .env securely (not in git; use secrets manager)
- Enable container auto-restart (Docker compose, Kubernetes)

## Performance Characteristics

| Operation | Latency | CPU | Memory |
|-----------|---------|-----|--------|
| Bot startup | 1-2s | Low | +50MB (JSON load) |
| /today command | 0.5s | Low | Negligible |
| Message formatting | 0.2s | Low | Negligible |
| Daily warning | 0.5s | Low | Negligible |
| Health check | 10ms | Very Low | Negligible |
| Escape function (1000 chars) | 5ms | Low | Negligible |

**Bottlenecks:**
1. Telegram API latency (not in our control)
2. JSON file size (minimal; pre-scraped data)
3. Regex escaping (negligible for message sizes)

## Technology Stack Justification

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3 | Quick iteration, large library ecosystem |
| Bot Framework | python-telegram-bot | Async support, job queue, active community |
| Web Server | Flask | Minimal overhead, health endpoint only |
| Data Format | JSON | Human-readable, fast parsing, no DB setup |
| Timezone | pytz | Handles DST, standard Python library |
| Scraping | BeautifulSoup | Robust HTML parsing, Vietnamese support |

## Future Architecture Enhancements

1. **Database Layer** (SQLite/PostgreSQL)
   - Store calendar data persistently
   - User preference persistence
   - Query analytics

2. **Cache Layer** (Redis)
   - Distributed caching for multi-instance deployments
   - Reduce JSON load times

3. **Message Queue** (Celery/RabbitMQ)
   - Decouple command processing from Telegram sends
   - Retry failed sends automatically

4. **Monitoring Stack** (Prometheus + Grafana)
   - Metrics collection
   - Alert on bot downtime
   - Visualize usage trends

5. **API Gateway** (FastAPI)
   - RESTful calendar API (not just Telegram)
   - Webhook support for 3rd-party integrations

6. **Background Jobs** (APScheduler)
   - Refresh calendar data periodically
   - Clean up old data

## References

- [python-telegram-bot Documentation](https://python-telegram-bot.readthedocs.io/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)

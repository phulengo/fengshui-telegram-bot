# Project Overview & PDR

**Project:** Fengshui Warning Bot
**Version:** 1.0
**Status:** Stable
**Release Date:** 2025-01-07
**Author:** @phulengo

## Executive Summary

A Telegram bot providing daily Feng Shui guidance based on Vietnamese lunar calendar. Users receive comprehensive daily readings including:
- Solar/lunar date conversion
- Auspicious/inauspicious hours (giờ tốt/giờ xấu)
- Five Elements (Ngũ Hành) analysis
- Lucky/unlucky stars and zodiac age warnings
- Travel directions (Hỷ thần, Tài thần)

**Target Users:** Vietnamese expats, Feng Shui practitioners, cultural enthusiasts

## Functional Requirements

### FR1: Daily Feng Shui Reading Service
- **Requirement:** Bot delivers comprehensive daily reading on user command (`/today`)
- **Data Included:**
  - Solar & lunar dates with heavenly stem/branch
  - 12 two-hour periods (Tí, Sửu, Dần, etc.) categorized as good/bad
  - Year, day, season five elements with thriving/suppressed indicators
  - Daily star name and zodiac animal
  - Auspicious (🔴) and inauspicious (⚫️) stars with notes
  - Age groups to avoid (tuổi kỵ)
  - Lucky travel directions
- **Acceptance:** User sees formatted, complete Feng Shui data within 2 seconds of `/today` command

### FR2: Scheduled Daily Warning
- **Requirement:** Bot broadcasts warning at 07:00 daily (Asia/Bangkok timezone)
- **Content:** Zodiac age warnings + inauspicious stars for the day
- **Target:** Pre-configured CHAT_ID (user or group)
- **Acceptance:** Warning delivers at 07:00 ±5 minutes, contains all required fields

### FR3: Telegram Bot Commands
- **`/start`** - Welcome message with bot description
- **`/today`** - Triggers daily Feng Shui reading
- **Acceptance:** Both commands respond within 2 seconds, correct message format

### FR4: Data Accuracy
- **Requirement:** Calendar data reflects actual Vietnamese lunar calendar
- **Sources:** Verified Vietnamese calendar websites (thoigian.com.vn, licham.vn, baomoi.com)
- **Coverage:** Minimum September 2025 - January 2026
- **Acceptance:** Calendar dates match official lunar calendar; star names verified by domain experts

### FR5: Message Formatting
- **Requirement:** All messages use Telegram MarkdownV2 format correctly
- **Special Handling:**
  - Emoji indicators (🔴 good, ⚫️ bad, 🌱🌞🍂❄️ seasons)
  - Escaped special characters (_, *, [, ], (, ), etc.)
  - Bold section headers for readability
  - Hierarchical formatting with └ connectors
- **Acceptance:** Messages render without escape errors; formatting matches mockup

## Non-Functional Requirements

### NR1: Performance
- **Response Time:** User commands must respond ≤2 seconds
- **Memory:** Application footprint ≤100MB at runtime
- **Startup:** Bot ready within 5 seconds of launch
- **Data Load:** 12-month calendar JSON loads within 1 second

### NR2: Reliability
- **Uptime:** Bot resilience to network hiccups; auto-retry on failed sends (3× with backoff)
- **Error Handling:** Graceful degradation if date not in database; return "No data found for today"
- **Health Check:** `/health` endpoint responds within 1 second for container orchestration

### NR3: Maintainability
- **Code Structure:** Modular functions (formatting, escaping, scheduling) for easy updates
- **Documentation:** All functions documented with purpose and parameters
- **Config Management:** Environment variables for sensitive data (tokens, chat IDs)
- **Extensibility:** Star mappings and exceptions configurable without code recompile

### NR4: Security
- **Token Protection:** TELEGRAM_TOKEN in .env (never committed)
- **No Logging:** Sensitive bot data not logged to console/files
- **Input Validation:** Bot ignores invalid commands gracefully
- **Data Isolation:** No user data retention between sessions

### NR5: Scalability
- **Chat Support:** Bot handles requests from multiple users/groups concurrently
- **Job Queue:** Scheduled tasks do not block command handlers
- **Horizontal Ready:** Health endpoint enables deployment to cloud (Docker, Kubernetes)

## Technical Specifications

### Technology Stack
- **Language:** Python 3.x
- **Framework:** python-telegram-bot (async with job queue)
- **Server:** Flask (health endpoint)
- **Data:** JSON (pre-scraped calendar cache)
- **Timezone:** Asia/Bangkok (UTC+7)
- **Deployment:** Containerized (health check ready)

### Integration Points
- **Telegram Bot API:** Polling mode, no webhooks
- **Calendar Data:** Three Vietnamese sources (scraped, cached locally)
- **Time Scheduling:** Job queue runs at 07:00 daily UTC+7

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Pre-scraped JSON cache | Avoids repeated network calls; fast startup |
| Emoji-based status | Visual distinction for auspicious/inauspicious without markup bloat |
| MarkdownV2 strict escaping | Telegram requires escape sequences; custom logic ensures correctness |
| Polling over webhooks | Simpler deployment; no firewall/public IP requirements |
| Daemon health server | Enables cloud deployment; easy liveness probes |
| Single-threaded bot | Sufficient for expected concurrency; simpler error handling |

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Message Delivery Rate | 99%+ | Monitor send failures vs attempts |
| Daily Warning Consistency | 100% | Confirm 07:00 delivery for 30 days |
| Command Response Time | <2s | Log request/response timestamps |
| Data Accuracy | 100% | Spot-check calendar dates vs official lunar calendar |
| Bot Uptime | 99%+ | Monitor health endpoint |
| User Satisfaction | N/A (v1) | Collect feedback for v2 |

## Phased Roadmap

### Phase 1: Core Release (v1.0) ✅
- Bot commands (/start, /today)
- Daily scheduled warnings
- Calendar data for 2025-2026
- MarkdownV2 formatting
- Health check endpoint
- Documentation

### Phase 2: Enhancement (v1.1) - Future
- `/history` - Past Feng Shui readings
- `/config` - User timezone/alert time customization
- Multi-language support (Vietnamese, English, Chinese)
- Star name explanations and tips

### Phase 3: Advanced (v2.0) - Future
- Personal zodiac animal readings (/myzodiac)
- Lucky color/direction recommendations (/lucky)
- Integration with personal calendars
- Admin dashboard for metrics

## Constraints & Assumptions

| Constraint | Details |
|-----------|---------|
| Timezone Fixed | Bot assumes Asia/Bangkok UTC+7; all times hardcoded |
| Calendar Coverage | Data available Sep 2025 - Jan 2026 only |
| Vietnamese Only | All text strings in Vietnamese; no i18n layer |
| Manual Updates | Calendar data requires manual re-scrape for date extensions |
| No Persistence | No database; no user preference storage |
| Polling Mode | Bot pulls updates; no incoming webhooks supported |

| Assumption | Details |
|-----------|---------|
| Valid .env | TELEGRAM_TOKEN and CHAT_ID exist and are valid |
| Network Available | Bot has internet access for startup and scheduled jobs |
| Timezone Consistency | Deployment environment supports Asia/Bangkok timezone |
| Data Quality | Calendar source websites remain stable and accurate |

## Acceptance Criteria

- [x] Bot responds to /start with welcome message
- [x] Bot responds to /today with complete daily reading within 2 seconds
- [x] Daily warning broadcasts at 07:00 (±5 min) with age warnings + inauspicious stars
- [x] All messages render without MarkdownV2 escape errors
- [x] Health endpoint responds with 200 OK status
- [x] Bot handles missing dates gracefully ("No data found for today")
- [x] Code documented; README explains setup and usage
- [x] Environment variables properly configured (no hardcoded secrets)

## Release Notes (v1.0)

**Date:** 2025-01-07
**Status:** Stable

### Features
- Daily Feng Shui readings via `/today` command
- 07:00 daily warnings to configured chat
- MarkdownV2 formatted messages with emoji indicators
- Health check endpoint for container orchestration
- Pre-scraped calendar data for 2025-2026

### Known Limitations
- Vietnamese language only
- Calendar data limited to Sep 2025 - Jan 2026
- Manual re-scrape needed for date extensions
- No user preferences or customization

### Breaking Changes
None (first release)

## Contact & Support

- **Author:** @phulengo
- **Version:** 1.0
- **Last Updated:** 2025-01-07
- **Copyright:** © 2025 Fengshui Warning Bot

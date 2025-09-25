import json
import os
import threading
from datetime import datetime
import pytz
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from flask import Flask
import re

app = Flask(__name__)

BOT_VERSION = "1.0"
BOT_AUTHOR = "@phulengo"
BOT_COPYRIGHT = f"© 2025 Fengshui Warning Bot • v{BOT_VERSION} • by {BOT_AUTHOR}"


@app.route("/health")
def health():
    return {"status": "ok"}, 200


def start_health_server():
    port = int(os.environ.get("PORT", "8443"))
    app.run(host="0.0.0.0", port=port, use_reloader=False, debug=False)


load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

with open("lich_van_nien_thoigian_2025.json", "r", encoding="utf-8") as f:
    fengshui_data = json.load(f)


def clean_all(val):
    if isinstance(val, list):
        return "\n".join(str(v) for v in val)
    if isinstance(val, dict):
        return "\n".join(f"{k}: {v}" for k, v in val.items())
    return str(val) if val is not None else "N/A"


def escape_markdown_v2(text):
    """Real escape function for Telegram MarkdownV2."""
    if text is None:
        return ""
    if isinstance(text, list):
        return "\n".join(escape_markdown_v2(item) for item in text)
    if isinstance(text, dict):
        return "\n".join(
            f"{escape_markdown_v2(str(k))}: {escape_markdown_v2(str(v))}"
            for k, v in text.items()
        )
    text = str(text)
    # Escape backslash first
    text = text.replace("\\", "\\\\")
    # Escape all MarkdownV2 reserved chars
    escape_chars = r"_*\[\]()~`>#+-=|{}.!"
    text = re.sub("([%s])" % re.escape(escape_chars), r"\\\1", text)
    return text


def contains_escape(text):
    """Detects if string contains any MarkdownV2 escape sequence."""
    return bool(re.search(r"\\[_*\[\]()~`>#+\-=|{}.!]", str(text)))


def safe_bold(text):
    """Only bold if no MarkdownV2 escapes are present."""
    if contains_escape(text):
        return text
    return f"*{text}*"


def pretty_star_list(star_list):
    # Configurable: edit these sets to add/remove exceptions any time!
    exception_good = {
        "Thiên tài",
        "Địa tài",
        "Trực tinh",
        "Nguyệt đức hợp",
        "Sinh khí",
        "Mẫu thương",
        "Thiên mã",
        "Ngũ phú",
        "Phúc hậu",
        "Lộc khố",
        "Thiên phú",
        "Nguyệt tài",
    }  # Use 🧧
    exception_bad = {
        "Địa tặc",
        "Sát chủ",
        "Ngũ quỷ",
        "Đại hao (Tử khí,Quan phù)",
        "Quỷ khốc",
        "Vãng vong (Thổ kỵ)",
        "Thụ tử",
        "Trùng tang",
        "Tiểu hao",
        "Thiên cương (Diệt môn",
        "Cửu không",
        "Cửu Thổ Quỷ",
    }  # Use 🚨

    dot_map = {"🔴": "🍀", "⚫️": "⚠️"}
    exception_map = {"🔴": "🧧", "⚫️": "🚨"}

    out = []
    for item in star_list:
        for name, detail in item.items():
            # Remove original dot for lookup
            base_name = name.replace("🔴", "").replace("⚫️", "").strip()
            m = re.search(r"(🔴|⚫️)", name)
            icon = ""
            if m:
                orig_dot = m.group(1)
                if orig_dot == "🔴" and base_name in exception_good:
                    icon = exception_map[orig_dot]
                elif orig_dot == "⚫️" and base_name in exception_bad:
                    icon = exception_map[orig_dot]
                else:
                    icon = dot_map[orig_dot]
                item_name = f"{icon} {base_name}"
            else:
                item_name = name
            out.append(esc(item_name))
            for k, v in detail.items():
                if v:
                    out.append(f"└ {esc(v)}")
            out.append("└")
    return "\n".join(out)


def escape_leading_dash_per_line(text):
    # Escapes dash at the start of any line for MarkdownV2
    safe_lines = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("-"):
            leading_spaces = len(line) - len(stripped)
            safe_lines.append(" " * leading_spaces + "\\-" + stripped[1:])
        else:
            safe_lines.append(line)
    return "\n".join(safe_lines)


def format_time_fancy(times):
    seen = set()
    sections = []
    for t in times:
        t_str = str(t)
        m = re.match(r"([^\(]+)\(([^\)]+)\)\s*-\s*(.*?)\s*-\s*(🔴|⚫️)$", t_str)
        if m:
            name = m.group(1).strip()
            timerange = m.group(2).strip()
            desc = m.group(3).strip()
            icon = m.group(4)
            section = f"{icon} {name}\n" f"    └ {desc}\n" f"    └ ({timerange})"
        else:
            section = t_str
        if section not in seen:
            seen.add(section)
            sections.append(section)
    return "\n".join(sections)


async def start(update, context):
    await update.message.reply_text(
        "Hello! I'm your Feng Shui Bot. Use /today to get today's Feng Shui info."
    )


def move_dot_first(element):
    # For a value like "Hoả 🔴 - Phú Đăng Hoả" or "Kim ⚫ - Kim loại"
    import re

    # Find any colored dot (red, black, etc)
    m = re.search(r"(🔴|⚫️|🔵|🟢|🟡|🟤|⚪)", element)
    if m:
        dot = m.group(1)
        element = element.replace(dot, "").strip()
        return f"{dot} {element}"
    return element


def esc(x):
    return escape_markdown_v2(x)


def format_season_element(season_element):
    icon_map = {"Mùa Xuân": "🌱", "Mùa Hạ": "🌞", "Mùa Thu": "🍂", "Mùa Đông": "❄️"}
    out = []
    for season, val in season_element.items():
        icon = icon_map.get(season, "")
        season_with_icon = f"{season} {icon}".strip()
        out.append(esc(season_with_icon))
        if "Tiết khí" in val:
            tiet_khi_raw = val["Tiết khí"]
            tiet_khi_clean = tiet_khi_raw.split(":", 1)[-1].strip().replace("_", ", ")
            out.append(esc("└ Tiết khí: " + tiet_khi_clean))
        if "Vượng" in val:
            out.append(esc("└ Vượng: " + val["Vượng"]))
        if "Khắc" in val:
            out.append(esc("└ Khắc: " + val["Khắc"]))
    return "\n".join(out)


async def today(update, context):
    today_str = datetime.now(pytz.timezone("Asia/Bangkok")).strftime("%Y-%m-%d")
    data = fengshui_data.get(today_str)
    if not data:
        await update.message.reply_text("No data found for today.")
        return

    def esc(x):
        return escape_markdown_v2(x)

    divider_line = esc("─────────────────")

    msg_lines = [
        safe_bold(esc("📅 " + clean_all(data.get("date")).upper())),
        safe_bold(esc("🌙  ÂM LỊCH:")),
        esc(clean_all(data.get("lunar-date")))
        + "\n"
        + esc("└ " + clean_all(data.get("detail-lunar-date"))),
        divider_line,
        safe_bold(esc("🕑 GIỜ TỐT:")),
        esc(format_time_fancy(data.get("good-time", []))),
        safe_bold(esc("🕑 GIỜ XẤU:")),
        esc(format_time_fancy(data.get("bad-time", []))),
        divider_line,
        safe_bold(esc("☯️ NGŨ HÀNH:")),
        safe_bold(esc("⏳ Năm:")),
        esc(move_dot_first(clean_all(data.get("year-element")))),
        safe_bold(esc("⏳ Ngày:")),
        esc(move_dot_first(clean_all(data.get("date-element")))),
        safe_bold(esc("⏳ Mùa")),
        format_season_element(data.get("season-element")),
        divider_line,
        safe_bold(esc("🌟 SAO:")),
        esc(data.get("star")),
        safe_bold(esc("🚫 Tuổi kỵ:")),
        ", ".join(esc(age) for age in data["bad-for-age"]),
        divider_line,
        safe_bold(esc("🔴 CÁT TINH:")),
        pretty_star_list(data.get("auspicious-star", [])),
        safe_bold(esc("⚫️ HUNG TINH:")),
        pretty_star_list(data.get("inauspicious-star", [])),
        divider_line,
        safe_bold(esc("🐾 ĐỘNG VẬT:")),
        esc(data["animal"]),
        safe_bold(esc("🧿 TRỰC:")),
        esc(
            clean_all(list(data["division"].keys())[0])
            + "\n└ "
            + clean_all(list(data["division"].values())[0])
        ),
        divider_line,
        safe_bold(esc("🧭 XUẤT HÀNH:")),
        safe_bold(esc("🧧 Hỷ thần:")) + " Hướng " + esc(data["depart"]["Hỷ thần"]),
        safe_bold(esc("💰 Tài thần:")) + " Hướng " + esc(data["depart"]["Tài thần"]),
    ]
    # footer & copyright
    msg_lines.append(divider_line)
    msg_lines.append(esc(BOT_COPYRIGHT))

    msg_full = "\n\n".join(msg_lines)
    msg_full = escape_leading_dash_per_line(msg_full)
    print(msg_full)  # Debug: print what will be sent to Telegram

    await update.message.reply_text(msg_full, parse_mode="MarkdownV2")


async def daily_warning(context):
    today_str = datetime.now(pytz.timezone("Asia/Bangkok")).strftime("%Y-%m-%d")
    data = fengshui_data.get(today_str)
    chat_id = context.job.data
    if data and "bad-for-age" in data:
        message = f"⚠️ Cảnh báo ngày {escape_markdown_v2(data['date'])} ({escape_markdown_v2(data['lunar-date'])})\n"
        message += f"🚫 Tuổi kỵ: {', '.join(escape_markdown_v2(age) for age in data['bad-for-age'])}\n"
        message += f"🔹 Lý do: Có các sao hung: {', '.join(escape_markdown_v2(star.get('name', str(star))) for star in data.get('inauspicious-star', []))}"
        await context.bot.send_message(
            chat_id=chat_id, text=message, parse_mode="MarkdownV2"
        )


def main():
    threading.Thread(target=start_health_server, daemon=True).start()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("today", today))
    application.job_queue.run_daily(
        daily_warning,
        time=datetime.strptime("07:00", "%H:%M").time(),
        data=CHAT_ID,
        days=(0, 1, 2, 3, 4, 5, 6),
    )
    application.run_polling()


if __name__ == "__main__":
    main()

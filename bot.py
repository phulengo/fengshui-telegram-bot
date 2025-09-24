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


@app.route("/health")
def health():
    return {"status": "ok"}, 200


def start_health_server():
    port = int(os.environ.get("PORT", "8443"))
    app.run(host="0.0.0.0", port=port, use_reloader=False)


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
    out = []
    for item in star_list:
        for name, detail in item.items():
            parts = []
            for k, v in detail.items():
                if v:
                    parts.append(f"{escape_markdown_v2(k)} {escape_markdown_v2(v)}")
            whole = " \\| ".join(parts)
            # Escape dash at start
            line = f"- {escape_markdown_v2(name)}: {whole}"
            # Check and escape leading dash for MarkdownV2
            if line.lstrip().startswith("-"):
                line = "\\-" + line.lstrip()[1:]
            out.append(line)
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


async def start(update, context):
    await update.message.reply_text(
        "Hello! I'm your Feng Shui Bot. Use /today to get today's Feng Shui info."
    )


async def today(update, context):
    today_str = datetime.now(pytz.timezone("Asia/Bangkok")).strftime("%Y-%m-%d")
    data = fengshui_data.get(today_str)
    if not data:
        await update.message.reply_text("No data found for today.")
        return

    def esc(x):
        return escape_markdown_v2(x)

    msg_lines = [
        safe_bold(
            esc(
                "📅 "
                + clean_all(data.get("date"))
                + " ("
                + clean_all(data.get("lunar-date"))
                + ")"
            )
        ),
        esc("──────────────────────"),
        safe_bold(esc("🕑 Giờ tốt:")),
        esc(data.get("good-time", [])),
        safe_bold(esc("🕑 Giờ xấu:")),
        esc(data.get("bad-time", [])),
        esc("──────────────────────"),
        safe_bold(esc("🔹 Chi tiết:")),
        esc(data.get("detail-lunar-date")),
        safe_bold(esc("🔹 Ngũ hành năm:")),
        esc(data.get("year-element")),
        safe_bold(esc("🔹 Ngũ hành ngày:")),
        esc(data.get("date-element")),
        safe_bold(esc("🔹 Ngũ hành mùa:")),
        esc(data.get("season-element")),
        esc("──────────────────────"),
        safe_bold(esc("🌟 Sao:")),
        esc(data.get("star")),
        safe_bold(esc("✅ Sao cát:")),
        pretty_star_list(data.get("auspicious-star", [])),
        safe_bold(esc("❌ Sao hung:")),
        pretty_star_list(data.get("inauspicious-star", [])),
        esc("──────────────────────"),
        safe_bold(esc("🐾 Con vật:")),
        esc(data["animal"]),
        safe_bold(esc("🔸 Trực:")),
        esc(
            clean_all(list(data["division"].keys())[0])
            + " \\- "
            + clean_all(list(data["division"].values())[0])
        ),
        safe_bold(esc("💰 Hỷ thần:")),
        esc(data["depart"]["Hỷ thần"]),
        safe_bold(esc("💰 Tài thần:")),
        esc(data["depart"]["Tài thần"]),
        safe_bold(esc("🚫 Tuổi kỵ:")),
        ", ".join(esc(age) for age in data["bad-for-age"]),
    ]
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

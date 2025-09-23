# bot.py

import json
import os
import threading
from datetime import datetime
import pytz
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

# NEW: minimal Flask server for health checks
from flask import Flask

app = Flask(__name__)

@app.route("/health")
def health():
    return {"status": "ok"}, 200

def start_health_server():
    # Render sets PORT; default local fallback
    port = int(os.environ.get("PORT", "8443"))
    # Host 0.0.0.0 so Render can expose it
    app.run(host="0.0.0.0", port=port)

# Existing bot code
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

async def start(update, context):
    await update.message.reply_text(
        "Hello! I'm your Feng Shui Bot. Use /today to get today's Feng Shui info."
    )

async def today(update, context):
    today_str = datetime.now(pytz.timezone('Asia/Bangkok')).strftime("%Y-%m-%d")
    data = fengshui_data.get(today_str)
    if not data:
        await update.message.reply_text("No data found for today.")
        return

    good_time_table = data.get("good-time", [])
    bad_time_table = data.get("bad-time", [])
    msg_lines = [
        f"📅 {clean_all(data.get('date'))} ({clean_all(data.get('lunar-date'))})",
        "──────────────────────",
        f"🕑 Giờ tốt:\n{clean_all(good_time_table)}",
        f"🕑 Giờ xấu:\n{clean_all(bad_time_table)}",
        "──────────────────────",
        f"🔹 Chi tiết:\n{clean_all(data.get('detail-lunar-date'))}",
        f"🔹 Ngũ hành năm:\n{clean_all(data.get('year-element'))}",
        f"🔹 Ngũ hành ngày:\n{clean_all(data.get('date-element'))}",
        f"🔹 Ngũ hành mùa:\n{clean_all(data.get('season-element'))}",
        "──────────────────────",
        f"🌟 Sao:\n{clean_all(data.get('star'))}",
        f"✅ Sao cát:\n{', '.join(clean_all(star.get('name', str(star))) for star in data.get('auspicious-star', []))}",
        f"❌ Sao hung:\n{', '.join(clean_all(star.get('name', str(star))) for star in data.get('inauspicious-star', []))}",
        "──────────────────────",
        f"🐾 Con vật:\n{clean_all(data.get('animal'))}",
        f"🔸 Trực:\n{clean_all(list(data.get('division', {}).keys())[0])}- {clean_all(list(data.get('division', {}).values())[0])}",
        f"💰 Hỷ thần:\n{clean_all(data.get('depart', {}).get('Hỷ thần'))}",
        f"💰 Tài thần:\n{clean_all(data.get('depart', {}).get('Tài thần'))}",
        f"🚫 Tuổi kỵ:\n{', '.join(clean_all(age) for age in data.get('bad-for-age', []))}"
    ]
    await update.message.reply_text("\n\n".join(msg_lines))

async def daily_warning(context):
    today_str = datetime.now(pytz.timezone('Asia/Bangkok')).strftime("%Y-%m-%d")
    data = fengshui_data.get(today_str)
    chat_id = context.job.data
    if data and "bad-for-age" in data:
        message = f"⚠️ Cảnh báo ngày {data['date']} ({data['lunar-date']})\n"
        message += f"🚫 Tuổi kỵ: {', '.join(data['bad-for-age'])}\n"
        message += f"🔹 Lý do: Có các sao hung: {', '.join(star.get('name', str(star)) for star in data.get('inauspicious-star', []))}"
        await context.bot.send_message(chat_id=chat_id, text=message)

def main():
    # Start the health server in a separate thread
    threading.Thread(target=start_health_server, daemon=True).start()

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("today", today))

    # Daily job, 7:00 Thailand time
    application.job_queue.run_daily(
        daily_warning,
        time=datetime.strptime("07:00", "%H:%M").time(),
        data=CHAT_ID,
        days=(0, 1, 2, 3, 4, 5, 6)
    )

    # Polling keeps the bot connected to Telegram
    application.run_polling()

if __name__ == '__main__':
    main()

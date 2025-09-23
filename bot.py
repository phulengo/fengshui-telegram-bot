from telegram.ext import Application, CommandHandler
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Load data once at startup
with open("lich_van_nien_thoigian_2025.json", "r", encoding="utf-8") as f:
    fengshui_data = json.load(f)

async def start(update, context):
    await update.message.reply_text("Hello! I'm your Feng Shui Bot. Use /check to get daily warnings. Use /today to get today's Feng Shui info.")

async def today(update, context):
    today_str = datetime.now(pytz.timezone('Asia/Bangkok')).strftime("%Y-%m-%d")
    data = fengshui_data.get(today_str)
    if not data:
        await update.message.reply_text("No data found for today.")
        return

    # Format a simple summary for Telegram
    good_time_table = "\n".join(f"🕑 {t}" for t in data['good-time'])
    bad_time_table = "\n".join(f"🕑 {t}" for t in data['bad-time'])

    def clean_braces(text):
        if isinstance(text, str):
            return text.replace("{", "").replace("}", "")
        return text

    def clean_all(text):
        if isinstance(text, str):
            return text.replace("{", "").replace("}", "").replace("'", "").replace("&", "")
        return text

    msg_lines = [
        f"📅 {clean_all(data['date'])} ({clean_all(data['lunar-date'])})",
        "──────────────────────",
        f"🔹 Chi tiết:\n{clean_all(data['detail-lunar-date'])}",
        f"🔹 Ngũ hành năm:\n{clean_all(data['year-element'])}",
        f"🔹 Ngũ hành ngày:\n{clean_all(data['date-element'])}",
        f"🔹 Ngũ hành mùa:\n{clean_all(str(data.get('season-element', 'N/A')))}",
        "──────────────────────",
        f"🕑 Giờ tốt:\n{clean_all(good_time_table)}",
        f"🕑 Giờ xấu:\n{clean_all(bad_time_table)}",
        "──────────────────────",
        f"🌟 Sao:\n{clean_all(data['star'])}",
        f"✅ Sao cát:\n{', '.join(clean_all(star.get('name', str(star))) for star in data.get('auspicious-star', []))}",
        f"❌ Sao hung:\n{', '.join(clean_all(star.get('name', str(star))) for star in data.get('inauspicious-star', []))}",
        "──────────────────────",
        f"🐾 Con vật:\n{clean_all(data['animal'])}",
        f"🔸 Trực:\n{clean_all(list(data['division'].keys())[0])} - {clean_all(list(data['division'].values())[0])}",
        f"💰 Hỷ thần:\n{clean_all(data['depart']['Hỷ thần'])}",
        f"💰 Tài thần:\n{clean_all(data['depart']['Tài thần'])}",
        f"🚫 Tuổi kỵ:\n{', '.join(clean_all(age) for age in data['bad-for-age']))}"
    ]
    msg = "\n\n".join(msg_lines)
    await update.message.reply_text(msg)

async def daily_warning(context):
    today_str = datetime.now(pytz.timezone('Asia/Bangkok')).strftime("%Y-%m-%d")
    data = fengshui_data.get(today_str)
    if data and "bad-for-age" in data and context.job.context:
        chat_id = context.job.context
        message = f"⚠️ Cảnh báo ngày {data['date']} ({data['lunar-date']})\n"
        message += f"🚫 Tuổi kỵ: {', '.join(data['bad-for-age'])}\n"
        message += f"🔹 Lý do: Có các sao hung: {', '.join(star.get('name', str(star)) for star in data.get('inauspicious-star', []))}"
        await context.bot.send_message(chat_id=chat_id, text=message)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("today", today))
    # Schedule daily warning at 7 AM Thailand time
    job_queue = application.job_queue
    job_queue.run_daily(daily_warning, time=datetime.strptime("07:00", "%H:%M").time(), context=CHAT_ID, days=(0, 1, 2, 3, 4, 5, 6))
    application.run_polling()

if __name__ == '__main__':
    main()
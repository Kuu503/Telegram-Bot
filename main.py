import os
import asyncio
import re
import yt_dlp
import edge_tts
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction

# --- WEB SERVER FOR RENDER ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is Running!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- BOT CONFIGURATION ---
TOKEN = "8551586940:AAEdh9CRA0Xtz7WCGQ4O8pp4VeqlgbDXk-I"
VOICE_NAME = "my-MM-ZawZawNeural" # Zawzaw အသံ (Nilar အတွက် my-MM-NilarNeural ပြောင်းပါ)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Server ပေါ်မှာ ၂၄ နာရီ Bot အဆင်သင့်ဖြစ်ပါပြီ။")

async def process_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text: return

    if "tiktok.com" in text:
        msg = await update.message.reply_text("⏳ ဗီဒီယိုဒေါင်းနေပါတယ်...")
        v_file = f"vid_{update.effective_user.id}.mp4"
        ydl_opts = {'format': 'best', 'outtmpl': v_file, 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([text])
            with open(v_file, "rb") as f:
                await update.message.reply_video(video=f, caption="✅ ဒေါင်းလုဒ်ဆွဲပြီးပါပြီ။")
            await msg.delete()
        except Exception as e:
            await msg.edit_text(f"❌ Video Error: {str(e)}")
        finally:
            if os.path.exists(v_file): os.remove(v_file)
    else:
        a_file = f"voice_{update.effective_user.id}.mp3"
        try:
            communicate = edge_tts.Communicate(text, VOICE_NAME)
            await communicate.save(a_file)
            with open(a_file, "rb") as f:
                await update.message.reply_audio(audio=f, title="AI Voice", performer="Zawzaw")
        except Exception as e:
            await update.message.reply_text(f"❌ TTS Error: {str(e)}")
        finally:
            if os.path.exists(a_file): os.remove(a_file)

def main():
    # Web server ကို thread တစ်ခုနဲ့ run မယ်
    Thread(target=run_web).start()
    
    # Bot ကို စတင် run မယ်
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_media))
    print("--- Bot Started ---")
    application.run_polling()

if __name__ == "__main__":
    main()

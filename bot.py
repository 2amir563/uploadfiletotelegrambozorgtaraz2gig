import os
import sys
import asyncio
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message

# اطلاعات اکانت و ربات تلگرام
API_ID = int(os.getenv("API_ID", "1234567"))
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

# حداکثر حجم هر پارت (1.8 گیگابایت به بایت)
MAX_SIZE_BYTES = 1800 * 1024 * 1024

app = Client("file_uploader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def split_file_fast(file_path):
    """Taksim kardane file haye bozorg tar az 1.8GB bedoone fesherde sazi baraye hefze sorat"""
    file_size = os.path.getsize(file_path)
    if file_size <= MAX_SIZE_BYTES:
        return [file_path], False

    base_dir = os.path.dirname(file_path) or "."
    base_name = os.path.basename(file_path)
    output_archive = os.path.join(base_dir, f"{base_name}.7z")

    # Switche -mx0 yani bedoone fesherde sazi (Haddaksar sorat)
    cmd = ["7z", "a", "-v1800m", "-mx0", output_archive, file_path]
    subprocess.run(cmd, check=True)

    parts = []
    for f in sorted(os.listdir(base_dir)):
        if f.startswith(f"{base_name}.7z"):
            parts.append(os.path.join(base_dir, f))

    if os.path.exists(file_path):
        os.remove(file_path)

    return parts, True

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    await message.reply_text("👋 Salam! Lotfan linke mostagim baraye download va upload ersal konid.")

@app.on_message(filters.text & filters.private)
async def handle_download(client, message: Message):
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        await message.reply_text("❌ Lotfan yak linke mo'tabar ersal konid.")
        return

    status_msg = await message.reply_text("⏳ Dar hale download e file rooye server...")
    file_name = os.path.basename(url.split("?")[0]) or "downloaded_file"
    output_path = os.path.join(os.getcwd(), file_name)

    # Download ba aria2c baraye sorate balatar
    cmd = ["aria2c", "-x", "16", "-s", "16", "-o", file_name, url]
    proc = await asyncio.create_subprocess_exec(*cmd)
    await proc.wait()

    if not os.path.exists(output_path):
        await status_msg.edit_text("❌ Download ba khata movajeh shod.")
        return

    await status_msg.edit_text("⚙️ Dar hale barresi e hajme file va amade sazi...")

    try:
        parts, is_split = split_file_fast(output_path)
        total_parts = len(parts)

        for idx, part_path in enumerate(parts, start=1):
            part_name = os.path.basename(part_path)
            caption = f"📦 Part {idx} az {total_parts}\n📄 `{part_name}`" if is_split else f"📄 `{part_name}`"
            
            await status_msg.edit_text(f"📤 Dar hale upload e Part {idx} az {total_parts} be Telegram...")
            
            await client.send_document(
                chat_id=message.chat.id,
                document=part_path,
                caption=caption
            )
            
            # Pak kardane part ba'd az upload baraye khali shodane space server
            if os.path.exists(part_path):
                os.remove(part_path)

        await status_msg.edit_text("✅ Upload ba movafaghiat tamam shod.")

    except Exception as e:
        await status_msg.edit_text(f"❌ Khataei rokh dad: {str(e)}")
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    app.run()

import os
import aiohttp
import requests
import json
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyromod import listen
from config import api_id, api_hash, bot_token, auth_users

bot = Client("bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

START_IMG = "https://graph.org/file/8b1f4146a8d6b43e5b2bc-be490579da043504d5.jpg"

@bot.on_message(filters.command("start"))
async def start(_, m):
    btns = [
        [InlineKeyboardButton("📚 Careerwill PUBLIC", callback_data="careerwill_public")],
        [InlineKeyboardButton("🔑 Careerwill PAID (Login)", callback_data="careerwill_paid")],
        [InlineKeyboardButton("📘 Utkarsh PUBLIC", callback_data="utkarsh_public")],
        [InlineKeyboardButton("🔑 Utkarsh PAID (Login)", callback_data="utkarsh_paid")],
    ]
    await m.reply_photo(
        START_IMG,
        caption="**Welcome! Extract all course links as .txt:**\n- Public: No login\n- Paid: Login required",
        reply_markup=InlineKeyboardMarkup(btns)
    )

# --- CAREERWILL PUBLIC ---
@bot.on_callback_query(filters.regex("^careerwill_public$"))
async def careerwill_public(_, cq):
    await cq.answer()
    msg = await cq.message.reply("Fetching Careerwill PUBLIC courses, please wait...")
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://elearn.crwilladmin.com/api/v1/batch/all"
            async with session.get(url) as resp:
                data = await resp.json()
            batches = data.get("data", [])
            links = []
            for batch in batches:
                name = batch.get("name", "Unknown")
                batch_id = batch.get("id", "N/A")
                link = f"https://elearn.crwilladmin.com/batch-detail/{batch_id}"
                links.append(f"{name}: {link}")
            if not links:
                await msg.edit("No public batches found.")
                return
            with open("careerwill_courses.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(links))
            await msg.reply_document("careerwill_courses.txt", caption="All Careerwill PUBLIC course links!")
            os.remove("careerwill_courses.txt")
            await msg.delete()
    except Exception as e:
        await msg.edit(f"Error: {e}")

# --- CAREERWILL PAID ---
@bot.on_callback_query(filters.regex("^careerwill_paid$"))
async def careerwill_paid(bot, cq):
    await cq.answer()
    m = cq.message
    prompt = await m.reply("Send your Careerwill **ID*Password** (e.g., `user@example.com*password123`):")
    try:
        creds = await bot.listen(m.chat.id)
        user, pwd = creds.text.split("*")
    except Exception:
        await m.reply("❌ Invalid format. Please send as `ID*Password`.")
        return
    login_url = "https://elearn.crwilladmin.com/api/v1/login-other"
    info = {
        "deviceType": "android",
        "password": pwd,
        "deviceModel": "TelegramBot",
        "deviceVersion": "Bot",
        "email": user,
    }
    try:
        r = requests.post(login_url, data=info)
        token = r.json()["data"]["token"]
    except Exception as e:
        await m.reply(f"❌ Login failed: {e}")
        return
    batches_url = f"https://elearn.crwilladmin.com/api/v1/comp/my-batch?&token={token}"
    try:
        batches = requests.get(batches_url).json()["data"]["batchData"]
        links = []
        for batch in batches:
            name = batch.get("batchName", "Unknown")
            batch_id = batch.get("id", "N/A")
            link = f"https://elearn.crwilladmin.com/batch-detail/{batch_id}"
            links.append(f"{name}: {link}")
        if not links:
            await m.reply("No paid batches found.")
            return
        with open("careerwill_paid.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(links))
        await m.reply_document("careerwill_paid.txt", caption="Your Careerwill paid course links!")
        os.remove("careerwill_paid.txt")
    except Exception as e:
        await m.reply(f"❌ Error fetching batches: {e}")

# --- UTKARSH PUBLIC ---
@bot.on_callback_query(filters.regex("^utkarsh_public$"))
async def utkarsh_public(_, cq):
    await cq.answer()
    msg = await cq.message.reply("Fetching Utkarsh PUBLIC courses, please wait...")
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://live-wsuser.e-utkarsh.com/api/getBooksListForUser"
            headers = {"siteId": "1"}
            async with session.post(url, headers=headers, data={}) as resp:
                data = await resp.json()
            books_json = data.get("books", "[]")
            books = json.loads(books_json)
            links = []
            for book in books:
                title = book.get("title", "Unknown")
                book_id = book.get("id", "N/A")
                link = f"https://utkarsh.com/book-detail/{book_id}"
                links.append(f"{title}: {link}")
            if not links:
                await msg.edit("No public books/courses found.")
                return
            with open("utkarsh_courses.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(links))
            await msg.reply_document("utkarsh_courses.txt", caption="All Utkarsh PUBLIC course links!")
            os.remove("utkarsh_courses.txt")
            await msg.delete()
    except Exception as e:
        await msg.edit(f"Error: {e}")

# --- UTKARSH PAID ---
@bot.on_callback_query(filters.regex("^utkarsh_paid$"))
async def utkarsh_paid(bot, cq):
    await cq.answer()
    m = cq.message
    prompt = await m.reply("Send your Utkarsh **ID*Password** (e.g., `user@example.com*password123`):")
    try:
        creds = await bot.listen(m.chat.id)
        user, pwd = creds.text.split("*")
    except Exception:
        await m.reply("❌ Invalid format. Please send as `ID*Password`.")
        return
    login_url = "https://live-wsshop.e-utkarsh.com/log/login"
    data = {"username": user, "password": pwd, "siteId": "1"}
    try:
        r = requests.post(login_url, data=data)
        token = r.json()["access_token"]
    except Exception as e:
        await m.reply(f"❌ Login failed: {e}")
        return
    books_url = "https://live-wsuser.e-utkarsh.com/api/getBooksListForUser"
    headers = {"X-Auth-Token": token}
    try:
        books_response = requests.post(books_url, headers=headers).json()
        books = json.loads(books_response.get("books", "[]"))
        links = []
        for book in books:
            title = book.get("title", "Unknown")
            book_id = book.get("id", "N/A")
            link = f"https://utkarsh.com/book-detail/{book_id}"
            links.append(f"{title}: {link}")
        if not links:
            await m.reply("No paid books/courses found.")
            return
        with open("utkarsh_paid.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(links))
        await m.reply_document("utkarsh_paid.txt", caption="Your Utkarsh paid course links!")
        os.remove("utkarsh_paid.txt")
    except Exception as e:
        await m.reply(f"❌ Error fetching books: {e}")

if __name__ == "__main__":
    bot.run()

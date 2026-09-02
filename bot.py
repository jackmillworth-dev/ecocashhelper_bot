import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
USER_ID = os.environ.get("TELEGRAM_USER_ID")

bot_app = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am running 24/7 on Railway.")

async def handle_form_submission(request):
    """Handle form submissions from website"""
    try:
        data = await request.json()
        
        # Format the message
        message = f"""📝 **New Form Submission**

Name: {data.get('name', 'N/A')}
Email: {data.get('email', 'N/A')}
Phone: {data.get('phone', 'N/A')}
Date of Birth: {data.get('dob', 'N/A')}"""
        
        # Send message via bot
        await bot_app.bot.send_message(chat_id=int(USER_ID), text=message)
        
        return web.json_response({"success": True})
    except Exception as e:
        print(f"Error: {e}")
        return web.json_response({"success": False, "error": str(e)}, status=400)

async def health_check(request):
    return web.json_response({"status": "ok"})

async def start_http_server():
    """Start HTTP server"""
    web_app = web.Application()
    web_app.router.add_post('/submit', handle_form_submission)
    web_app.router.add_get('/', health_check)
    
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 3000)
    await site.start()
    print("HTTP server started on port 3000")

async def main():
    global bot_app
    
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set")
        return
    
    if not USER_ID:
        print("ERROR: TELEGRAM_USER_ID not set")
        return
    
    # Create bot
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    
    # Start HTTP server in background
    asyncio.create_task(start_http_server())
    
    print("Bot starting...")
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()

if __name__ == "__main__":
    asyncio.run(main())

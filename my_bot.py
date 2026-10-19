from telethon import TelegramClient, events
from qrcode import QRCode
import asyncio
import telethon.errors
import json
import os

# Application Settings
APP_ID = 123456  # Replace with your actual API ID
APP_HASH = 'YOUR_API_HASH'
PHONE_NUMBER = 'YOUR_PHONE_NUMBER'
SETTINGS_FILE = 'settings.json'

def read_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {
        "reply_text": "I am currently busy and cannot reply. I will write as soon as I am free.",
        "attachment_url": None
    }

def write_settings(reply_text: str, attachment_url: str | None) -> None:
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as file:
        json.dump({"reply_text": reply_text, "attachment_url": attachment_url}, file, ensure_ascii=False, indent=4)

settings = read_settings()
DEFAULT_RESPONSE = settings["reply_text"]
ATTACHMENT_URL = settings["attachment_url"]

is_autoreply_enabled = False

client = TelegramClient('user_session', APP_ID, APP_HASH)

def generate_qr_code(token: str) -> None:
    qr = QRCode()
    qr.add_data(token)
    qr.print_ascii()

@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event: events.NewMessage.Event) -> None:
    global is_autoreply_enabled
    current_user = await client.get_me()
    
    is_contact = getattr(event.sender, 'contact', False) if event.sender else False
    
    if event.is_private and event.sender_id != current_user.id and not is_contact:
        if is_autoreply_enabled:
            await asyncio.sleep(5) 
            
            if ATTACHMENT_URL:
                await event.respond(file=ATTACHMENT_URL, message=DEFAULT_RESPONSE)
            else:
                await event.respond(DEFAULT_RESPONSE)
                
            print(f"Auto-reply sent to ID: {event.sender_id}")

@client.on(events.NewMessage(outgoing=True))
async def handle_command(event: events.NewMessage.Event) -> None:
    global is_autoreply_enabled, DEFAULT_RESPONSE, ATTACHMENT_URL
    current_user = await client.get_me()
    
    if event.chat_id == current_user.id:
        command_text = event.text.strip()
        
        if command_text == '/on':
            is_autoreply_enabled = True
            await event.edit("✅ Auto-responder ENABLED")
        elif command_text == '/off':
            is_autoreply_enabled = False
            await event.edit("❌ Auto-responder DISABLED")
            
        elif command_text.startswith('/settext '):
            DEFAULT_RESPONSE = command_text.replace('/settext ', '', 1)
            write_settings(DEFAULT_RESPONSE, ATTACHMENT_URL)
            await event.edit(f"✅ Text updated and saved:\n{DEFAULT_RESPONSE}")
            
        elif command_text.startswith('/setphoto '):
            ATTACHMENT_URL = command_text.replace('/setphoto ', '', 1)
            write_settings(DEFAULT_RESPONSE, ATTACHMENT_URL)
            await event.edit("✅ Photo added and saved!")
            
        elif command_text == '/clearphoto':
            ATTACHMENT_URL = None
            write_settings(DEFAULT_RESPONSE, ATTACHMENT_URL)
            await event.edit("✅ Photo removed and saved.")

async def start_bot() -> None:
    await client.connect()

    if not await client.is_user_authorized():
        print("\n--- AUTHORIZATION REQUIRED ---")
        qr_login = await client.qr_login()

        while not await client.is_user_authorized():
            generate_qr_code(qr_login.url)
            print("\nScan the QR code above in Telegram.")
            
            try:
                await qr_login.wait(timeout=20)
            except asyncio.TimeoutError:
                print("\nQR code expired. Generating a new one...")
                await qr_login.recreate()
            except telethon.errors.SessionPasswordNeededError:
                password = input("Enter your 2FA password: ")
                await client.sign_in(password=password)
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                break

    print("\nBot started. Running in background.")
    print(f"Current text: {DEFAULT_RESPONSE}")
    print(f"Current photo: {ATTACHMENT_URL}")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(start_bot())
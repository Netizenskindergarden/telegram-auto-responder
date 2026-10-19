# Telegram Auto-Responder Userbot

A Python-based Telegram userbot that automatically replies to incoming private messages. Built with the Telethon library.

## Features
- Secure QR-code authorization (no phone code required).
- Anti-spam delay before sending a reply.
- Ignores contacts to prevent replying to friends/family.
- Dynamic configuration: text and photo can be changed via commands in "Saved Messages".
- Settings are saved in a JSON file, so they persist after restart.

## Commands
- `/on` — Enable auto-responder
- `/off` — Disable auto-responder
- `/settext <text>` — Set custom reply text
- `/setphoto <url>` — Set attachment URL
- `/clearphoto` — Remove attachment

## Tech Stack
- Python
- Telethon
- asyncio
- JSON
- qrcode

## Installation
1. Install dependencies:
   ```bash
   pip install telethon qrcode
   python bot.py

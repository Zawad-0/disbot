# disbot

Office energy monitor for lights and fans, with one shared backend feeding a live web dashboard and a Discord bot.

## What It Does

- Simulates three office rooms: Drawing Room, Work Room 1, and Work Room 2.
- Tracks each room's two fans and three lights, for 15 simulated devices total.
- Stores status, wattage, room, and last state-change timestamp for every device.
- Serves live data through FastAPI.
- Shows a dashboard with room status, power usage, alerts, and demo toggles.
- Adds Discord commands for real backend data before falling back to Groq-powered chat.

Note: the project brief says 18 devices, but the listed hardware breakdown is 3 rooms x (2 fans + 3 lights), which equals 15 devices. The simulator follows the explicit room/device breakdown.

## Repository Layout

```text
disbot/
  api.py              FastAPI backend and dashboard host
  simulator.py        Single source of truth for simulated devices
  commands.py         Discord command parsing and response formatting
  backend_client.py   Bot client for backend API calls
  conversation.py     Lightweight chat memory
  groq_client.py      Groq API client
web/
  index.html          Live dashboard
  styles.css
  app.js
docs/
  system-diagram.txt
  hardware-schematic.md
tests/
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill in `.env` for Discord and Groq:

```text
DISCORD_TOKEN=your_discord_bot_token
DISCORD_ALERT_CHANNEL_ID=optional_channel_id
GROQ_API_KEY=your_groq_key
BACKEND_URL=http://127.0.0.1:8000
```

## Run the Backend and Dashboard

```powershell
uvicorn disbot.api:app --reload
```

Open `http://127.0.0.1:8000` to view the dashboard.

Useful API routes:

- `GET /api/devices`
- `GET /api/summary`
- `GET /api/rooms/drawing`
- `GET /api/rooms/work1`
- `GET /api/rooms/work2`
- `GET /api/alerts`
- `POST /api/devices/{device_id}/toggle`

## Run the Discord Bot

Start the backend first, then run:

```powershell
python bot.py
```

Supported commands:

| Command | Action |
| :--- | :--- |
| `!status` | Shows ON fan/light counts and watts per room. |
| `!room drawing` | Shows every device in the Drawing Room. |
| `!room work1` | Shows every device in Work Room 1. |
| `!room work2` | Shows every device in Work Room 2. |
| `!usage` | Shows current watts and estimated daily kWh. |

Other messages are sent to Groq with lightweight per-user conversation history.

## Alerts

The backend flags:

- Devices left on outside 9 AM to 5 PM.
- Devices left on for at least 2 hours.

The bot can post high-severity alerts every five minutes when `DISCORD_ALERT_CHANNEL_ID` is configured.

## Tests

```powershell
python -m unittest discover
```

## Deliverables Notes

- High-level system diagram: `docs/system-diagram.txt`
- Representative circuit notes: `docs/hardware-schematic.md`
- Demo path: start backend, open dashboard, toggle devices, run Discord commands.

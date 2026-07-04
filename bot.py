from __future__ import annotations

import asyncio
import os

import discord
from dotenv import load_dotenv

from disbot.backend_client import BackendClient
from disbot.commands import parse_command
from disbot.conversation import ConversationMemory
from disbot.groq_client import GroqClient


load_dotenv()

backend = BackendClient(os.getenv("BACKEND_URL", "http://127.0.0.1:8000"))
groq = GroqClient()
memory = ConversationMemory()

class OfficeMonitorClient(discord.Client):
    async def setup_hook(self) -> None:
        asyncio.create_task(alert_loop())


intents = discord.Intents.default()
intents.message_content = True
client = OfficeMonitorClient(intents=intents)


@client.event
async def on_ready() -> None:
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    command_response = parse_command(message.content, backend.summary, backend.room)
    if command_response:
        await message.channel.send(command_response)
        return

    user_id = str(message.author.id)
    memory.add(user_id, "user", message.content)
    system_context = {
        "role": "system",
        "content": "You are disbot, a concise office energy monitoring assistant. Use explicit commands for live device data.",
    }
    reply = groq.chat([system_context, *memory.history(user_id)])
    memory.add(user_id, "assistant", reply)
    await message.channel.send(reply[:1900])


async def alert_loop() -> None:
    await client.wait_until_ready()
    channel_id = os.getenv("DISCORD_ALERT_CHANNEL_ID")
    while not client.is_closed():
        if channel_id:
            channel = client.get_channel(int(channel_id))
            if channel:
                for alert in backend.alerts():
                    if alert["severity"] == "high":
                        await channel.send(f"Alert: {alert['message']}")
        await asyncio.sleep(300)


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN is required")
    client.run(token)


if __name__ == "__main__":
    main()

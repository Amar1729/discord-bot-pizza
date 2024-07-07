#! /usr/bin/env python3

from __future__ import annotations

import json
import os
from pathlib import Path

import discord
from dotenv import load_dotenv

PIZZA_FILE = Path("./pizza-users.json")

load_dotenv()

TOKEN = os.environ["TOKEN"]

"""Run the bot."""
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
# client = commands.Bot(command_prefix="$", intents=intents)


class Pizza:
    """Simple class to faciliate "database" access."""

    _pizza_file = Path("./pizza-users.json")

    @staticmethod
    def _read() -> list[dict[str, str | bool]]:
        with Pizza._pizza_file.open() as f:
            return json.load(f)

    @staticmethod
    def _write(obj) -> None:
        with Pizza._pizza_file.open("w") as f:
            json.dump(obj, f)

    @staticmethod
    def users() -> list[str]:
        return [str(obj["name"]) for obj in Pizza._read()]

    @staticmethod
    def set_user(user: str) -> None:
        content = Pizza._read()
        for obj in content:
            if obj["name"] == user:
                break
        else:
            print(f"User not found in users: {user}")
            return

        for obj in content:
            obj["current"] = obj["name"] == user

        Pizza._write(content)

    @staticmethod
    def next() -> None:
        content = Pizza._read()

        for idx, obj in enumerate(content):
            current = obj["current"]

            if current:
                next_idx = (idx + 1) % len(content)
                break
        else:
            print("No current user found?")
            return

        content[idx]["current"] = False
        content[next_idx]["current"] = True

        Pizza._write(content)

    @staticmethod
    def text() -> str:
        content = Pizza._read()

        return "\n".join([
            ("-> " if obj["current"] else " ") + str(obj["name"])
            for obj in content
        ])


@client.event
async def on_ready() -> None:
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message) -> None:
    if message.author == client.user:
        return

    if message.content.lower() == "next pizza":
        Pizza.next()
        return

    if message.content.lower() == "pizza":
        await message.channel.send(Pizza.text())


if __name__ == "__main__":
    client.run(TOKEN)

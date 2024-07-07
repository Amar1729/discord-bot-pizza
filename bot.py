#! /usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import discord
from dotenv import load_dotenv

PIZZA_FILE = Path("./pizza-users.json")

if not Path("./.env").exists():
    raise RuntimeError("Must have a local .env file, specifiying TOKEN.")

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
    def _entry(user: str, current: bool = False) -> dict[str, str | bool]:
        return {"name": user, "current": current}

    @staticmethod
    def add_user(user: str) -> None:
        if not Pizza._pizza_file.exists():
            Pizza._write([Pizza._entry(user, current=True)])
            return

        if user not in Pizza.users():
            content = Pizza._read()
            content.append(Pizza._entry(user))
            Pizza._write(content)
            return

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
    def next(jumps: int = 1) -> None:
        content = Pizza._read()

        for idx, obj in enumerate(content):
            current = obj["current"]

            if current:
                next_idx = (idx + jumps) % len(content)
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

    if message.content.lower().startswith("next pizza"):
        try:
            jumps = int(message.content.split(" ")[-1]) % 4
        except ValueError:
            jumps = 1
        Pizza.next(jumps)
        return

    if message.content.lower() == "pizza":
        await message.channel.send(Pizza.text())


def main_cli() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--print", action="store_true")
    parser.add_argument("--add-user", help="username to add")
    parser.add_argument("--set-current", choices=Pizza.users(), help="user to set as current")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        client.run(TOKEN)

    elif args.print:
        print(Pizza.text())

    elif args.add_user:
        Pizza.add_user(args.add_user)

    elif args.set_current:
        Pizza.set_user(args.set_current)


if __name__ == "__main__":
    main_cli()

import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "user_warnings.db")


def create_user_table():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "users_per_guild" (
            "user_id"    INTEGER,
            "warning_count"  INTEGER,
            "guild_id"   INTEGER,
            PRIMARY KEY("user_id", "guild_id")
        );
    """)

    connection.commit()
    connection.close()


create_user_table()

def increase_and_get_warnings(user_id: int, guild_id: int):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT warning_count FROM users_per_guild
        WHERE (user_id = ?) AND (guild_id = ?);
    """, (user_id, guild_id))

    result = cursor.fetchone()

    if result == None:
        cursor.execute("""
            INSERT INTO users_per_guild (user_id, warning_count, guild_id)
            VALUES (?, 1, ?);
        """, (user_id, guild_id))

        connection.commit()
        connection.close()
        return 1
    
    cursor.execute("""
        UPDATE users_per_guild SET warning_count = ?
        WHERE (user_id = ?) AND (guild_id = ?);
    """, (user_id, guild_id))


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} is online!!")


bot.run(TOKEN)

import discord
import os
import asyncpg
import asyncio
import psycopg2
from database.database import database
from os.path import join, dirname
from dotenv import load_dotenv
from discord.ext import commands

# TODO:
#       Let users change thread embed color
#       purge command

def prefix_callable(bot_client, message):
    try:
        sql = database(bot_client.prefix)
        prefix = sql.get_prefix(message.guild)
        return prefix[0]
    except:
        return '.'

bot = commands.Bot(command_prefix=prefix_callable, case_insensitive=True)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user}")
    sql = database(bot.db)
    count = await sql.get_all_thread_channels()
    activ = discord.Activity(type=discord.ActivityType.watching, name=f"{count} threads | {len(bot.guilds)} guilds")
    await bot.change_presence(activity=activ)


@bot.command(hidden=True)
@commands.is_owner()
async def reload_cog(ctx, cog):
    bot.reload_extension(cog)
    await ctx.send("Reload successful.")


load_dotenv('thread_bot.env')
bot_token = os.getenv('TOKEN')
db = os.getenv('DATABASE')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASS')

DB_SETTINGS = {
    'host': 'localhost',
    'database': db,
    'user': user,
    'password': password,
}

cogs = ['cogs.makethread',
        'cogs.editthread',
        'cogs.lock_thread',
        'cogs.embeds',
        'cogs.utils', 
        'cogs.create_category', 
        'cogs.errors'
        ]


for cog in cogs:
    bot.load_extension(cog)


db_loop = asyncio.get_event_loop()
bot.prefix = psycopg2.connect(**DB_SETTINGS)
bot.db = db_loop.run_until_complete(asyncpg.create_pool(**DB_SETTINGS, max_inactive_connection_lifetime=480))

async def populate():
     sql = database(bot.db)
     bot.thread_check_cache = await sql.get_thread_channels()

loop = asyncio.get_event_loop()
loop.run_until_complete(populate())

bot.run(bot_token, reconnect=True)

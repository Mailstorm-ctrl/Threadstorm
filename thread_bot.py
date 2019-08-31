import discord
import os
import asyncpg
import asyncio
import psycopg2
import random
from database.database import database
from os.path import join, dirname
from dotenv import load_dotenv
from discord.ext import commands

def prefix_callable(bot_client, message):
    try:
        sql = database(bot_client.prefix)
        prefix = sql.get_prefix(message.guild)
        return prefix
    except:
        return '!'

bot = commands.Bot(command_prefix=prefix_callable, case_insensitive=True)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user}")
    activities = [f'with {len(bot.all_channels)} topics', "Let's Talk."]
    await bot.change_presence(activity=discord.Game(random.choice(activities)))

@bot.command()
@commands.is_owner()
async def reload_cog(ctx, cog):
    try:
        bot.reload_extension(cog)
        await ctx.send("Reload successful.")
    except Exception as e:
        nl = '\n'
        await ctx.send(f"Error with reload.{nl}{e}")

load_dotenv('thread_bot.env')
bot_token = os.getenv('TOKEN')
db = os.getenv('DATABASE')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASS')

cogs = ['cogs.makethread','cogs.editthread','cogs.lock_thread','cogs.embeds','cogs.utils']
for cog in cogs:
    bot.load_extension(cog)

async def populate():
    bot.prefix = psycopg2.connect(host='localhost', database=db, user=user, password=password)
    bot.db = await asyncpg.connect(host='localhost', database=db, user=user, password=password)
    sql = database(bot.db)
    bot.all_channels = await sql.get_all_threads()
    bot.thread_categories = await sql.get_thread_category_ids()
    bot.thread_channels = await sql.get_thread_channels()
    bot.last_message = await sql.get_last_messages()

loop = asyncio.get_event_loop()
loop.run_until_complete(populate())

bot.run(bot_token, reconnect=True)
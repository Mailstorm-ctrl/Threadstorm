import discord
import asyncpg
import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands

# Known issues:
# Sometimes it wont post the warning for a channel delete   Cause: I blame rate limits
# Sometimes it wont delete a channel                        Cause: Above

def prefix_callable(bot_client, message):
    try:
        return bot_client.cache[message.guild.id]['prefix']
    except:
        return '.'

bot = commands.Bot(command_prefix=prefix_callable, case_insensitive=True)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user}")
    active_threads = 0
    for k,v in bot.cache.items():
        active_threads += len(v['active_threads'])
    activity = discord.Activity(type=discord.ActivityType.watching,
                                name=f"{active_threads} threads | {len(bot.guilds)} guilds")
    await bot.change_presence(activity=activity)

@bot.command(hidden=True)
@commands.is_owner()
async def reload_cog(ctx, cog):
    bot.reload_extension(f"cogs.{cog}")
    await ctx.message.add_reaction('👍')


load_dotenv('threadstorm.env')
bot_token = os.getenv('TOKEN')
db = os.getenv('DATABASE')
edb = os.getenv('ERROR_DB')
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
        'cogs.create_category',
        'cogs.utils',
        'cogs.settings',
        'cogs.errors',
        'cogs.updates'
        ]

    
for cog in cogs:
    print(f'loaded cog: {cog}')
    bot.load_extension(cog)

async def write_to_db(guild):
    #Write everything in cache to database. By guild only, obviously
    async with bot.db.acquire() as con:
        await con.execute('INSERT INTO ts_data(guild_id, data) VALUES($1, $2) ON CONFLICT (guild_id) DO UPDATE SET data=$2', guild.id, json.dumps(bot.cache[guild.id], default=str))

async def populate_cache():
    """Populate the bots cache. Convert everything just in case"""
    bot.cache = {}
    async with bot.db.acquire() as con:
        results = await con.fetch('SELECT * FROM ts_data;')
    for data in results:
        guild_data = json.loads(data[1])
        try:
            bot.cache[data[0]] = {}
            bot.cache[data[0]]['prefix'] = guild_data.get('prefix')
            bot.cache[data[0]]['default_thread_channel'] = int(guild_data.get('default_thread_channel'))
            bot.cache[data[0]]['settings'] = {}
            bot.cache[data[0]]['settings']['role_required'] = bool(guild_data.get('settings').get('role_required'))
            bot.cache[data[0]]['settings']['allowed_roles'] = [int(r_id) for r_id in guild_data.get('settings').get('allowed_roles')]
            bot.cache[data[0]]['settings']['TTD'] = int(guild_data.get('settings').get('TTD'))
            bot.cache[data[0]]['settings']['cleanup'] = bool(guild_data.get('settings').get('cleanup'))
            bot.cache[data[0]]['settings']['admin_roles'] = [int(r_id) for r_id in guild_data.get('settings').get('admin_roles')]
            bot.cache[data[0]]['settings']['admin_bypass'] = bool(guild_data.get('settings').get('admin_bypass'))
            bot.cache[data[0]]['settings']['cooldown'] = {}
            bot.cache[data[0]]['settings']['cooldown']['enabled'] = bool(guild_data.get('settings').get('cooldown').get('enabled'))
            bot.cache[data[0]]['settings']['cooldown']['rate'] = int(guild_data.get('settings').get('cooldown').get('rate'))
            bot.cache[data[0]]['settings']['cooldown']['per'] = int(guild_data.get('settings').get('cooldown').get('rate'))
            bot.cache[data[0]]['settings']['cooldown']['bucket'] = guild_data.get('settings').get('cooldown').get('bucket')
            bot.cache[data[0]]['active_threads'] = {}
            for thread,value in guild_data.get('active_threads').items():
                bot.cache[data[0]]['active_threads'][int(thread)] = {}
                try:
                    bot.cache[data[0]]['active_threads'][int(thread)]['last_message_time'] = datetime.strptime(value.get('last_message_time'),"%Y-%m-%d %H:%M:%S.%f")
                except:
                    bot.cache[data[0]]['active_threads'][int(thread)]['last_message_time'] = datetime.strptime(f"{value.get('last_message_time')}.000111","%Y-%m-%d %H:%M:%S.%f")
                bot.cache[data[0]]['active_threads'][int(thread)]['keep'] = bool(value.get('keep'))
                bot.cache[data[0]]['active_threads'][int(thread)]['author_id'] = int(value.get('author_id'))
                if value.get('original_msg_id') is None:
                    bot.cache[data[0]]['active_threads'][int(thread)]['original_msg_id'] = 0
                else:
                    bot.cache[data[0]]['active_threads'][int(thread)]['original_msg_id'] = int(value.get('original_msg_id'))
                bot.cache[data[0]]['active_threads'][int(thread)]['json'] = bool(value.get('json'))

            bot.cache[data[0]]['custom_categories'] = {}
            for channel,value in guild_data.get('custom_categories').items():
                bot.cache[data[0]]['custom_categories'][int(channel)] = int(value)                
        except Exception as e:
            print(e)
            continue

db_loop = asyncio.get_event_loop()

bot.db = db_loop.run_until_complete(asyncpg.create_pool(**DB_SETTINGS, max_inactive_connection_lifetime=480))
bot.error_color = 0xcc0000
bot.success_color = 0x00b359
bot.warning_color = 0xffb366
bot.DEFAULT_COLOR = 0x00ace6
bot.write_db = write_to_db

bot.cooldowns = {}
for guild in bot.guilds:
    bot.cooldowns[guild.id] = {}

loop = asyncio.get_event_loop()
loop.run_until_complete(populate_cache())

bot.run(bot_token, reconnect=True)

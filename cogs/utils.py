import discord
import time
import copy
from cogs.embeds import TB_Embeds
from database.database import database
from discord.ext import tasks, commands

class TB_Utils(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channel_checker.start()
        self.integrity_check.start()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        thread_category = discord.utils.get(guild.categories, name='THREADS')
        sql = database(self.bot.db)
        if thread_category is None:
            thread_category = await guild.create_category('THREADS', reason='Initial category of threads creation.')
        await sql.joined_guild(guild, thread_category)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return
        if not message.author.bot:
            if message.channel.id in self.bot.thread_check_cache.get(message.guild.id):
                sql = database(self.bot.db)
                await sql.update_last_message(message.channel)

    @commands.command(name='setup', aliases=['tsetup'])
    @commands.has_permissions(manage_guild=True)
    async def create_guild_join(self, ctx):
        thread_category = discord.utils.get(ctx.guild.categories, name='THREADS')
        sql = database(self.bot.db)
        if thread_category is None:
            thread_category = await ctx.guild.create_category('THREADS', reason='Initial category of threads creation.')
        await sql.joined_guild(ctx.guild, thread_category)
        await ctx.send('Setup ran. Guild added to database.')

    @commands.command(name='prefix', aliases=['tprefix'])
    @commands.has_permissions(manage_roles=True)
    async def update_prefix(self, ctx, prefix: str):
        sql = database(self.bot.db)
        await sql.update_prefix(ctx.guild, prefix)
        await ctx.send(f"Prefix updated to: {prefix}")
        return

    @commands.command(name='help')
    async def thelp(self, ctx): # Yes I know bad. Use built-in help, don't hard-code yada
        embed = await TB_Embeds.thelp(ctx)
        await ctx.send(embed=embed)

    @tasks.loop(count=1)
    async def integrity_check(self):
        sql = database(self.bot.db)
        configured_guilds = await sql.get_guilds()
        for guild in self.bot.guilds:
            if guild.id not in configured_guilds:
                try:
                    category = await guild.create_category('Threads', reason='Initial category of threads creation.')
                    await sql.joined_guild(guild, category)
                except:
                    continue

    @integrity_check.before_loop
    async def wait2(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=24.0)
    async def channel_checker(self):
        """ Function loop that fetches channels that have been inactive for 3 to 4 days.
        For channels that have had no activity for 3 days, go through and lock it.
        For channels that have had no activity for 4 days, delete them."""
        sql = database(self.bot.db)
        await sql.delete_thread_old()
        channels = await sql.get_half_dead_channels()
        for channel in channels:
            try:
                channel_found = True
                thread_channel = self.bot.get_channel(channel)
                if thread_channel is None:
                    try:
                        thread_channel = await self.bot.fetch_channel(channel)
                    except:
                        channel_found = False
                if channel_found:
                    embed = await TB_Embeds.inactive_lock(thread_channel)
                    await thread_channel.send(embed=embed)
                    for role in thread_channel.overwrites:
                        await thread_channel.set_permissions(role, send_messages=False)
            except Exception as e:
                print(f'Exception in half_dead channels: {e}')
                continue
        
        channels = await sql.get_full_dead_channels()
        for channel in channels:
            try:
                channel_found = True
                thread_channel = self.bot.get_channel(channel)
                if thread_channel is None:
                    try:
                        thread_channel = await self.bot.fetch_channel(channel)
                    except:
                        channel_found = False
                if channel_found:
                    await thread_channel.delete(reason='Inactivity delete/cleanup')
            except Exception as e:
                print(f'Exception in full_dead channels: {e}')
                continue

    @channel_checker.before_loop
    async def wait(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(TB_Utils(bot))

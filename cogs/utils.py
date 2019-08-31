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
        self.update_last_message.start()

    @commands.Cog.listener()
    async def on_guild_join(guild):
        thread_category = discord.utils.get(guild.text_channels, name='Threads')
        if thread_category is None:
            try:
                sql = database(self.bot.db)
                category = await guild.create_category('Threads', reason='Initial category of threads creation.')
                await database.joined_guild(guild, category)
            except:
                return

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return
        if not message.author.bot and message.channel.id in self.bot.thread_channels:
            self.bot.last_message[message.channel.id] = [message.guild.id, int(time.time())]

    @commands.command(name='prefix', aliases=['tprefix'])
    @commands.has_permissions(manage_roles=True)
    async def update_prefix(self, ctx, prefix: str):
        sql = database(self.bot.db)
        await sql.update_prefix(ctx.guild, prefix)
        await ctx.send(f"Prefix updated to: {prefix}")
        return

    @commands.command(name='source')
    async def source_code(self, ctx):
        embed=discord.Embed(
                            title="GitHub page", 
                            url="https://github.com/Mailstorm-ctrl/Thread-Bot", 
                            description="Here you go, have a nice look at this butt nasty code.", 
                            color=0xffffff
                            )
        embed.set_author(
                        name=self.bot.user.name,
                        icon_url=self.bot.user.avatar_url
                        )
        await ctx.send(embed=embed)

    @tasks.loop(hours=12.0)
    async def update_last_message(self):
        sql = database(self.bot.db)
        for k,v in self.bot.last_message.items():
            try:
                await sql.update_last_message(k,v)
            except:
                continue

    @update_last_message.before_loop
    async def wait2(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=24.0)
    async def channel_checker(self):
        sql = database(self.bot.db)
        looper = copy.deepcopy(self.bot.all_channels)
        for k,v in looper.items():
            try:
                var = self.bot.last_message.get(v[1])[1]
                if (int(time.time()) - var) >= 259200:
                    channel_found = True
                    thread = self.bot.get_channel(v[1])
                    if thread is None:
                        try:
                            thread = await self.bot.fetch_channel(v[1])
                        except:
                            channel_found = False
                            self.bot.all_channels.pop(k,None)
                            await sql.delete_thread(k)
                    
                    if channel_found:
                        try:
                            guild = self.bot.get_guild(v[0])
                            if guild is None:
                                guild = await self.bot.get_guild(v[0])
                            embed = TB_Embeds.inactive_lock(guild)
                            await thread.send(embed=embed)
                        except:
                            continue
                        for role in thread.guild.roles:
                            await thread.set_permissions(role,
                                                        send_messages=False,
                                                        reason='Inactive'
                                                        )
                
                if (int(time.time()) - var) >= 345600:
                    channel_found = True
                    thread = self.bot.get_channel(v[1])
                    if thread is None: #Channel not found in cache. Attempt to fetch it.
                        thread = await self.bot.fetch_channel(v[1])
                    
                    if thread is None:
                        channel_found = False
                        self.bot.all_channels.pop(k,None)
                        await sql.delete_thread(k)
                    
                    if channel_found:
                        try:
                            await thread.delete(reason='Inactivity')
                            self.bot.all_channels.pop(k,None)
                            await sql.delete_thread(k)
                        except:
                            continue
            except:
                continue

    @channel_checker.before_loop
    async def wait(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(TB_Utils(bot))
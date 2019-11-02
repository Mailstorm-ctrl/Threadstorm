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
        self.update_status.start()
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
        if message.guild is None or message.author.bot:
            return
        if message.content == self.bot.user.mention:
            try:
                sql = database(self.bot.prefix)
                prefix = sql.get_prefix(message.guild)
                embed = discord.Embed(title='Guild prefix:', description=f'{message.guild.name} uses the prefix: `{prefix[0]}` for all commands.', color=0x69dce3)
                embed.set_author(name=message.guild.name, icon_url=message.guild.icon_url)
                await message.channel.send(embed=embed)
            except:
                embed = discord.Embed(title='Guild prefix:', description=f'{message.guild.name} uses the prefix: `.` for all commands.', color=0x69dce3)
                embed.set_author(name=message.guild.name, icon_url=message.guild.icon_url)
                await message.channel.send(embed=embed)
            return
        try:
            if message.channel.id in self.bot.thread_check_cache.get(message.guild.id):
                    sql = database(self.bot.db)
                    await sql.update_last_message(message.channel)
        except TypeError:
            pass

    @commands.command(name='setup', aliases=['tsetup'], description='Initialize guild')
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    async def create_guild_join(self, ctx):
        """If for some reason your guild was NOT added to the database, this command will force your guild into it."""
        thread_category = discord.utils.get(ctx.guild.categories, name='THREADS')
        sql = database(self.bot.db)
        if thread_category is None:
            thread_category = await ctx.guild.create_category('THREADS', reason='Initial category of threads creation.')
        await sql.joined_guild(ctx.guild, thread_category)
        await ctx.send('Setup ran. Guild added to database.')

    @commands.command(name='prefix', aliases=['tprefix'], description='Sets the custom prefix')
    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def update_prefix(self, ctx, prefix: str):
        """Lets you modify the servers prefix. You must have the `manage_roles` permission to use this."""
        sql = database(self.bot.db)
        await sql.update_prefix(ctx.guild, prefix)
        await ctx.send(f"Prefix updated to: {prefix}")
        return

    @commands.command(name='help', aliases=['thelp'], hidden=True)
    async def new_help(self, ctx, *, cmd=None):
        if cmd is None:
            embed=discord.Embed(title=f"{ctx.bot.user.name} Help Menu", description=f"Need some help? Use `{ctx.prefix}thelp command` to get specific help", color=0x69dce3)
            embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
            cmd_list = {}
            for command in ctx.bot.commands:
                try:
                    if await command.can_run(ctx) and not command.hidden:
                        cmd_list[command.name] = command.description
                except discord.ext.commands.CommandError:
                    continue
            avail_cmds = []
            longest_command = max(cmd_list.keys(), key=len)
            for k,v in cmd_list.items():
                avail_cmds.append('`' + k + ' ' + '-'*(len(longest_command)-len(k)) + '->>` ' + v)
            avail_cmds = '\n'.join(sorted(avail_cmds))
            embed.add_field(name=f'Available Commands:', value=avail_cmds, inline=False)
            embed.add_field(name=f'Support Server', value='This bot has a support server! If you run into issues or have ideas, feel free to join. I listen to everything you have to say. Good and bad!\nInvite link: [discord.gg/M8DmU86](https://discord.gg/M8DmU86)', inline=False)
            embed.add_field(name='Want to help this bot grow?', value=f'Spread the word! You can also help by giving this bot a vote [here (top.gg)](https://top.gg/bot/617376702187700224/vote) or [here (botsfordiscord.com)](https://botsfordiscord.com/bot/617376702187700224/vote).', inline=False)
            embed.set_footer(text=f"Only commands you have permission to run in #{ctx.channel.name} are shown here.")
        else:
            help_cmd = ctx.bot.get_command(cmd)
            if help_cmd is None:
                await ctx.send("Unable to find that command. Run this again with no arguments for a list of commands.")
                return
            aliases = [alias for alias in help_cmd.aliases]
            embed = discord.Embed(title=f'{help_cmd.name.upper()} MAN PAGE', description=f'This is all the info you need for the `{ctx.prefix}{help_cmd.name}` command.', color=0x69dce3)
            embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
            embed.add_field(name='Alises for this command:', value=', '.join(aliases), inline=False)
            embed.add_field(name='Usage:', value=f'{ctx.prefix}{help_cmd.name} {help_cmd.signature}')
            embed.add_field(name='Description:', value=help_cmd.short_doc, inline=False)
        await ctx.send(embed=embed)

    @tasks.loop(count=1)
    async def integrity_check(self):
        sql = database(self.bot.db)
        configured_guilds = await sql.get_guilds()
        for guild in self.bot.guilds:
            if guild.id not in configured_guilds:
                try:
                    category = await guild.create_category('THREADS', reason='Initial category of threads creation. | Integrity Check')
                    await sql.joined_guild(guild, category)
                except:
                    continue

    @integrity_check.before_loop
    async def wait2(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=1.0)
    async def update_status(self):
        sql = database(self.bot.db)
        count = await sql.get_all_thread_channels()
        activ = discord.Activity(type=discord.ActivityType.watching, name=f"{count} threads | {len(self.bot.guilds)} guilds")
        try:
            await bot.change_presence(activity=activ)
        except:
            pass

    @update_status.before_loop
    async def wait3(self):
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
                    thread_permissions = {role.id:[thread_channel.overwrites.get(role).pair()[0].value, thread_channel.overwrites.get(role).pair()[1].value] for role in thread_channel.overwrites}
                    await sql.update_channel_permissions_by_channel(thread_channel, json.dumps(thread_permissions))
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

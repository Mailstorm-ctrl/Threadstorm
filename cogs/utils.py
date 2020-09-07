import discord
import typing
import copy
import asyncio
from datetime import datetime, timedelta
from discord.ext import tasks, commands

class TB_Utils(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.checker.start()
        self.update_status.start()
        self.integrity_check.start()

    # Maybe some day this will be supported
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Listen for category delete events and undo the damage if possible."""
        if channel.id in [self.bot.cache[channel.guild.id]['default_thread_channel']] + [channel_id for channel_id in self.bot.cache[channel.guild.id]['custom_categories'].keys()]:
            try:
                async for entry in channel.guild.audit_logs(limit=10, action=discord.AuditLogAction.channel_delete):
                    if channel.id == self.bot.cache[channel.guild.id]['default_thread_channel'] and entry.user.id != self.bot.user.id:
                        new_default = await channel.guild.create_category(name=channel.name, overwrites=channel.overwrites, reason=f"User: {entry.user.name} manually deleted default thread category.")
                        
                        for thread in self.bot.cache[channel.guild.id]['active_threads']:
                            try:
                                if self.bot.cache[channel.guild.id]['active_threads'][thread]['category'] == channel.id:
                                    channel_obj = self.bot.get_channel(thread)
                                    if channel_obj is None:
                                        continue
                                    await channel_obj.edit(category=new_default, reason=f"User: {entry.user.name} manually deleted default thread category. Fixing...")
                                    self.bot.cache[channel.guild.id]['active_threads'][thread]['category'] = new_default.id
                            except:
                                continue
                        
                        self.bot.cache[channel.guild.id]['default_thread_channel'] = new_default.id
                        await self.bot.write_db(channel.guild)
                        await entry.user.send("It seems like you deleted the category I use to put uncategorized threads in. I've recreated the channel but please don't do this.\n\nIf you want a different name, simply rename the channel. If you don't want people using the channel, restrict my permissions to custom categories only and a channel to issue admin commands in.")
                        break

                    if channel.id in self.bot.cache[channel.guild.id]['custom_categories'] and entry.user.id != self.bot.user.id:
                        
                        new_category = await channel.guild.create_category(name=channel.name, overwrites=channel.overwrites, reason=f"User: {entry.user.name} manually deleted category.")
                        hub_channel = self.bot.get_channel(self.bot.cache[channel.guild.id]['custom_categories'][channel.id])
                        if hub_channel is None:
                            hub_channel = await self.bot.fetch_channel(self.bot.cache[channel.guild.id]['custom_categories'][channel.id])
                        
                        await hub_channel.edit(category=new_category, reason=f"User: {entry.user.name} manually deleted a category. Fixing...")
                        # Get rid of the old k,v pair and replace with updated values
                        self.bot.cache[channel.guild.id]['custom_categories'].pop(channel.id, None)
                        self.bot.cache[channel.guild.id]['custom_categories'][new_category.id] = hub_channel.id
                        
                        for thread in self.bot.cache[channel.guild.id]['active_threads']:
                            try:
                                if self.bot.cache[channel.guild.id]['active_threads'][thread]['category'] == channel.id:
                                    channel_obj = self.bot.get_channel(thread)
                                    if channel_obj is None:
                                        continue
                                    await channel_obj.edit(category=new_category, reason=f"User: {entry.user.name} manually deleted a category. Fixing...")
                                    self.bot.cache[channel.guild.id]['active_threads'][thread]['category'] = new_category.id
                            except:
                                continue
                        
                        await self.bot.write_db(channel.guild)
                        await entry.user.send("It seems like you deleted a category I control. I've gone ahead and undid this but please consider using the proper commands to get rid of a category.")
                        break
            except Exception as e:
                # Need a way to warn that a category was deleted and the bot wasn't able to correct it
                pass
        else:
            pass
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Try and create the default place for threads. Else just fail silently. Continue to add guild to database with defaults"""
        self.bot.cache[guild.id] = {
                            "prefix" : ".",
                            "default_thread_channel" : 0,
                            "settings" : {
                                "role_required" : False,
                                "allowed_roles" : [],
                                "TTD" : 3,
                                "cleanup" : True,
                                "admin_roles" : [],
                                "admin_bypass" : False,
                                "cooldown" : {
                                    "enabled" : True,
                                    "rate" : 0,
                                    "per" : 0,
                                    "bucket" : "user"
                                    }
                                },
                            "active_threads" : {},
                            "custom_categories" : {}          
                            }
        try:
            category = await guild.create_category("THREADS", reason='Initial category of threads creation.')
            self.bot.cache[guild.id]["default_thread_channel"] = category.id
        except:
            self.bot.cache[guild.id]["default_thread_channel"] = 0
        await self.bot.write_db(guild)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author.bot:
            #if message.author.id == self.bot.user.id:
            #    await message.add_reaction('🗑️')
            return
        if message.content == self.bot.user.mention:
            try:
                embed = discord.Embed(title='Guild prefix:',
                                    description=f"{message.guild.name} uses the prefix: `{self.bot.cache[message.guild.id]['prefix']}` for all commands.",
                                    color=self.bot.DEFAULT_COLOR)
            except:
                embed = discord.Embed(title='Guild prefix:',
                                    description=f"{message.guild.name} uses the prefix: `.` for all commands.",
                                    color=self.bot.DEFAULT_COLOR)

            embed.set_author(name=message.guild.name, icon_url=message.guild.icon_url)
            await message.channel.send(embed=embed)
        try:
            if message.channel.id in self.bot.cache[message.guild.id]['active_threads']:
                self.bot.cache[message.guild.id]['active_threads'][message.channel.id]['last_message_time'] = datetime.now()
                await self.bot.write_db(message.guild)
        except:
            pass



    @commands.command(name='help', aliases=['thelp'], hidden=True)
    async def new_help(self, ctx, *, cmd=None):
        if cmd is None:
            embed=discord.Embed(title=f"{ctx.bot.user.name} Help Menu", description=f"Need some help? Use `{ctx.prefix}thelp command` to get specific help", color=self.bot.DEFAULT_COLOR)
            embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
            cmd_list = {}
            for command in ctx.bot.commands:
                try:
                    if await command.can_run(ctx) and not command.hidden:
                        cmd_list[command.name] = command.description
                except (discord.ext.commands.CommandError, IndexError):
                    continue
            avail_cmds = []
            longest_command = max(cmd_list.keys(), key=len)
            for k,v in cmd_list.items():
                avail_cmds.append('`' + k + ' ' + '-'*(len(longest_command)-len(k)) + '->>` ' + v)
            avail_cmds = '\n'.join(sorted(avail_cmds))
            embed.add_field(name=f'Available Commands:', value=avail_cmds, inline=False)
            embed.add_field(name=f'Support Server', value='This bot has a support server! If you run into issues or have ideas, feel free to join. I listen to everything you have to say. Good and bad!\nInvite link: [discord.gg/M8DmU86](https://discord.gg/M8DmU86)', inline=False)
            embed.add_field(name='Want to help this bot grow?', value=f'Spread the word! You can also help by giving this bot a vote [here (top.gg)](https://top.gg/bot/617376702187700224/vote) or [here (botsfordiscord.com)](https://botsfordiscord.com/bot/617376702187700224/vote).', inline=False)
            embed.add_field(name='Want to add this bot to your server?', value=f"Awesome! Just [click this link.](https://threadstorm.app/invite)")
            embed.set_footer(text=f"Only commands you have permission to run in #{ctx.channel.name} are shown here.")
        else:
            help_cmd = ctx.bot.get_command(cmd)
            if help_cmd is None:
                await ctx.send("Unable to find that command. Run this again with no arguments for a list of commands.")
                return
            aliases = [alias for alias in help_cmd.aliases]
            embed = discord.Embed(title=f'{help_cmd.name.upper()} MAN PAGE', description=f'This is all the info you need for the `{ctx.prefix}{help_cmd.name}` command.', color=self.bot.DEFAULT_COLOR)
            embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
            embed.add_field(name='Alises for this command:', value=', '.join(aliases), inline=False)
            embed.add_field(name='Usage:', value=f'{ctx.prefix}{help_cmd.name} {help_cmd.signature}')
            embed.add_field(name='Description:', value=help_cmd.short_doc, inline=False)
        await ctx.send(embed=embed)


    @commands.command(name='debug', aliases=['tdebug'], hidden=True, description="Provide guilds cache area")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def self_debug(self, ctx, channel: typing.Optional[str] = None):
        allowed = []
        allowed_admin = []
        categories = []

        for role in self.bot.cache[ctx.guild.id]['settings']['allowed_roles']:
            try:
                role = ctx.guild.get_role(role)
                allowed.append(role.name)
            except:
                pass
        for role in self.bot.cache[ctx.guild.id]['settings']['admin_roles']:
            try:
                role = ctx.guild.get_role(role)
                allowed_admin.append(role.name)
            except:
                pass
        for category in self.bot.cache[ctx.guild.id]['custom_categories']:
            try:
                category = ctx.guild.get_channel(category)
                categories.append(category.name)
            except:
                pass

        default_category = ctx.guild.get_channel(self.bot.cache[ctx.guild.id]['default_thread_channel'])
        if default_category is None:
            default_category = "Default category not found or error fetching channel name."
        else:
            default_category = default_category.name
        

        if not categories:
            categories.append("No custom categories or error fetching channels.")
        if not allowed:
            allowed.append("No roles defined or error fetching guild roles.")
        if not allowed_admin:
            allowed_admin.append("No roles defined or error fetching guild roles.")
        
        embed=discord.Embed(title=f"{ctx.guild.name} Debug Output", description="Here is all your guilds stored information, exluding active threads", color=self.bot.DEFAULT_COLOR)
        embed.set_author(name="Threadstorm", icon_url=ctx.bot.user.avatar_url)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="Guild ID", value=ctx.guild.id, inline=True)
        embed.add_field(name="Prefix", value=self.bot.cache[ctx.guild.id]['prefix'], inline=True)
        embed.add_field(name="Roles Required", value=f"`{self.bot.cache[ctx.guild.id]['settings']['role_required']}`", inline=True)
        embed.add_field(name="Allowed Roles", value=", ".join(allowed), inline=False)
        embed.add_field(name="Time-Till-Inactive", value=f"`{self.bot.cache[ctx.guild.id]['settings']['TTD']} Days`", inline=True)
        embed.add_field(name="Cleanup", value=f"`{self.bot.cache[ctx.guild.id]['settings']['cleanup']}`", inline=True)
        embed.add_field(name="Admin Bypass", value=f"`{self.bot.cache[ctx.guild.id]['settings']['admin_bypass']}`", inline=True)
        embed.add_field(name="Admin Roles", value=", ".join(allowed_admin), inline=False)
        embed.add_field(name="Custom Categories", value=", ".join(categories), inline=True)
        embed.add_field(name="Default Category", value=default_category, inline=True)
        embed.set_footer(text="Active threads are excluded due to potential character limits. Related information such as channel id's, the keep flag, the author of a thread and the first message id are also kept in memory and on a local database.")
        await ctx.send(embed=embed)

    @tasks.loop(count=1)
    async def integrity_check(self):
        for guild in self.bot.guilds:
            if guild.id not in self.bot.cache:
                self.bot.cache[guild.id] = {
                            "prefix" : ".",
                            "default_thread_channel" : 0,
                            "settings" : {
                                "role_required" : False,
                                "allowed_roles" : [],
                                "TTD" : 3,
                                "cleanup" : True,
                                "admin_roles" : [],
                                "admin_bypass" : False,
                                "cooldown" : {
                                    "rate" : 0,
                                    "per" : 0,
                                    "bucket" : "user"
                                    }
                                },
                            "active_threads" : {},
                            "custom_categories" : {}          
                            }
                try:
                    category = await guild.create_category("THREADS", reason='Initial category of threads creation.')
                    self.bot.cache[guild.id]["default_thread_channel"] = category.id
                except:
                    self.bot.cache[guild.id]["default_thread_channel"] = 0
                await self.bot.write_db(guild)

    @integrity_check.before_loop
    async def wait2(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=1.0)
    async def update_status(self):
        active_threads = 0
        for k,v in self.bot.cache.items():
            active_threads += len(v['active_threads'])
        activity = discord.Activity(type=discord.ActivityType.watching,
                                    name=f"{active_threads} threads | {len(self.bot.guilds)} guilds")
        await self.bot.change_presence(activity=activity)
    
    @update_status.before_loop
    async def wait3(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=24.0)
    async def checker(self):
        tlock = self.bot.get_command('lock')
        self.bot.last_run = datetime.now()
        for guild in self.bot.cache.keys():
            guild_obj = self.bot.get_guild(guild)
            if guild_obj is None:
                continue
            ttd = timedelta(days=self.bot.cache[guild]['settings']['TTD'])


            # Make a copy because we may potentially change the size of the loop
            working_loop = copy.deepcopy(self.bot.cache[guild]['active_threads'])
            for thread in working_loop:
                await asyncio.sleep(3)
                now = datetime.now()
                converted_last_msg = self.bot.cache[guild]['active_threads'][thread]['last_message_time']             
                expiration_date = converted_last_msg + ttd
                one_day_before_expiration = expiration_date - timedelta(days=1)

                if now >= expiration_date and not self.bot.cache[guild]['active_threads'][thread]['keep']:
                    thread_channel = guild_obj.get_channel(thread)
                    if thread_channel is None:
                        try:
                            thread_channel = await self.bot.fetch_channel(thread)
                            if thread_channel is None:
                                continue
                        except discord.errors.NotFound:
                            self.bot.cache[guild]['active_threads'].pop(thread, None)
                            await self.bot.write_db(guild_obj)
                    try:
                        await thread_channel.delete(reason=f"Thread expired")
                        self.bot.cache[guild]['active_threads'].pop(thread, None)
                        await self.bot.write_db(guild_obj)
                    #If it's any of these exceptions, don't bother trying again and just update cache/db
                    except (discord.NotFound, discord.Forbidden, AttributeError):
                        self.bot.cache[guild]['active_threads'].pop(thread, None)
                        await self.bot.write_db(guild_obj)
                    
                    # Try again in 24 hours. Some generic error happened
                    except discord.HTTPException:
                        pass
                    continue

                #It's about to be yoinked
                if (one_day_before_expiration <= now < expiration_date) and not self.bot.cache[guild]['active_threads'][thread]['keep']:
                    thread_channel = guild_obj.get_channel(thread)
                    if thread_channel is None:
                        try:
                            thread_channel = await self.bot.fetch_channel(thread)
                            if thread_channel is None:
                                continue
                        except discord.errors.NotFound:
                            self.bot.cache[guild]['active_threads'].pop(thread, None)
                            await self.bot.write_db(guild_obj)

                    # Call our lock command to lock the thread
                    try:
                        prefix = self.bot.cache[thread_channel.guild.id]['prefix']
                    except:
                        prefix = '.'
                    try:
                        await tlock.__call__(thread_channel, f'Inactive.\nUse {prefix}tkeep to keep this thread. Use {prefix}tunlock to unlock this thread. Otherwise this channel will be deleted in 24 hours.')
                        await thread_channel.send("If this is spamming your channel, sorry. I updated the bot and it hasn't gone as smooth as I'd like it to.")
                    except:
                        pass

    @checker.before_loop
    async def wait4(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(TB_Utils(bot))

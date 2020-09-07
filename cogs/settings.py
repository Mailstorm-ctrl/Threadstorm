import discord
from discord.ext import commands

class TB_Settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setup', aliases=['tsetup'], description='Initialize guild')
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    async def create_guild_join(self, ctx):
        """If for some reason your guild was NOT added to the database, this command will force your guild into it.\nWARNING: RUNNING THIS WILL ESSENTIALLY RESET YOUR GUILD. ACTIVE THREADS WILL BE LOST AND WILL NO LONGER BE MANAGED!"""
        category = discord.utils.get(ctx.guild.categories, name='THREADS')
        if category is None:
            try:
                category = await ctx.guild.create_category('THREADS', reason='Initial category of threads creation.')
            except (discord.HTTPException, discord.InvalidArgument):
                await ctx.send("Unable to create channel for threads. Please try creating a category manually and name it `THREADS`, then re-run this command.")
                return
        self.bot.cache[ctx.guild.id] = {
                            "prefix" : ".",
                            "default_thread_channel" : category.id,
                            "settings" : {
                                "role_required" : False,
                                "allowed_roles" : [],
                                "TTD" : 3,
                                "cleanup" : True,
                                "admin_roles" : [],
                                "admin_bypass" : False,
                                "cooldown" : {
                                    "enabled": True,
                                    "rate" : 0,
                                    "per" : 0,
                                    "bucket" : "user"
                                    }
                                },
                            "active_threads" : {},
                            "custom_categories" : {}          
                            }
        await ctx.send('Setup ran. Guild added to database.')
        await self.bot.write_db(ctx.guild)

    

    @commands.command(name='prefix', aliases=['tprefix'], description='Sets the custom prefix')
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def update_prefix(self, ctx, prefix: str):
        """Lets you modify the servers prefix. You must have the `manage_guild` permission to use this."""
        self.bot.cache[ctx.guild.id]['prefix'] = prefix
        embed=discord.Embed(title="Guild settings updated", description=f"You have changed the **prefix** for this guild.\nThe current prefix is: `{self.bot.cache[ctx.guild.id]['prefix']}`", color=self.bot.success_color)
        embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f"To issue commands, you must now type {self.bot.cache[ctx.guild.id]['prefix']} instead of {ctx.prefix} . Example: {self.bot.cache[ctx.guild.id]['prefix']}tmake")
        await self.bot.write_db(ctx.guild)
        await ctx.send(embed=embed)
        

    
    @commands.command(name='timetodead', aliases=['tttd'], description='Sets the period to wait before a thread becomes inactive, in days')
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def update_ttd(self, ctx, ttd):
        """Change the number of days the bot will wait before marking a channel for deletion. You must have the `manage_guild` permission to use this."""
        self.bot.cache[ctx.guild.id]['settings']['TTD'] = int(ttd)
        await self.bot.write_db(ctx.guild)
        await ctx.send(f"Inactivity time set to: {ttd} days")
        return


    @commands.command(name='roles', aliases=['troles','trolls'], description='Toggles and adds/removes roles from running `tmake` command.')
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def update_roles(self, ctx, *roles: discord.Role):
        """Running with no arguments will toggle whether a specific set of roles are required or not. If ran with arguments, the arguments should be role mentions, their names, or the role ID which will add or remove the role (Does not delete or modify server roles)."""
        if len(roles) == 0:
            self.bot.cache[ctx.guild.id]['settings']['role_required'] = not self.bot.cache[ctx.guild.id]['settings']['role_required']
            embed=discord.Embed(title="Guild settings updated", description=f"You have changed the **roles_required** flag for this guild.\nThe current value is: `{self.bot.cache[ctx.guild.id]['settings']['role_required']}`", color=self.bot.success_color)
            embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_footer(text=f"A True value means users need a specific(s) role in order to use {ctx.prefix}tmake. A False value means anyone in your server can make threads.")
            await ctx.send(embed=embed)
        else:
            added = []
            removed = []
            for role in roles:
                if role.id in self.bot.cache[ctx.guild.id]['settings']['allowed_roles']:
                    self.bot.cache[ctx.guild.id]['settings']['allowed_roles'].remove(role.id)
                    removed.append(f"- {role.name}")
                else:
                    self.bot.cache[ctx.guild.id]['settings']['allowed_roles'].append(role.id)
                    added.append(f"+ {role.name}")

            if not added:
                added.append("+ No roles added!")
            if not removed:
                removed.append("- No roles removed")

            added_list = "```patch\n"
            for role in added:
                added_list += f"{role}\n"
            added_list += "```"
            removed_list = "```patch\n"
            for role in removed:
                removed_list += f"{role}\n"
            removed_list += "```"

            current = []
            for role in self.bot.cache[ctx.guild.id]['settings']['allowed_roles']:
                cur = ctx.guild.get_role(role)
                current.append(cur.name)
            if not current:
                current.append("No configured roles.")

            embed = discord.Embed(title=f"{ctx.guild.name} Role Required List", description='The following is a summary of what roles you just added, removed and the current list of allowed roles.', color=self.bot.success_color)
            embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.add_field(name="ADDED", value=added_list, inline=False)
            embed.add_field(name="REMOVED", value=removed_list, inline=False)
            embed.add_field(name="CURRENT LIST", value=" | ".join(current), inline=False)
            embed.set_footer(text="Did you add your admin roles? This setting does not care about role or user permissions!")
            await ctx.send(embed=embed)
        await self.bot.write_db(ctx.guild)

    
    @update_roles.error
    async def ur_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            error_str = str(error)
            role_name = error_str[6:-12]
            message_list = ctx.message.content.split(' ')
            arg_list = message_list[1:]
            good_roles = []
            for arg in arg_list:
                good_roles.append(discord.utils.find(lambda r :  r.id == arg or r.name == arg or r.mention == arg, ctx.guild.roles))
            good_roles = [i for i in good_roles if i]
            if not good_roles:
                await ctx.send("ran out")



    @commands.command(name='aroles', aliases=['taroles'], description='Toggles and adds/removes admin roles from bypassing `tmake` command cooldown.')
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def update_aroles(self, ctx, *roles: discord.Role):
        """Running with no arguments will toggle whether admin roles are activate or not. If ran with arguments, the arguments should be role mentions, their names, or the role ID which will add or remove the role (Does not delete or modify server roles)."""
        if len(roles) == 0:
            self.bot.cache[ctx.guild.id]['settings']['admin_bypass'] = not self.bot.cache[ctx.guild.id]['settings']['admin_bypass']
            embed=discord.Embed(title="Guild settings updated", description=f"You have changed the **admin_bypass** flag for this guild.\nThe current value is: `{self.bot.cache[ctx.guild.id]['settings']['admin_bypass']}`", color=self.bot.success_color)
            embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_footer(text=f"A True value means admin roles can bypass the cooldown on {ctx.prefix}tmake. A False value means admin roles do not get to bypass the cooldown.")
            await ctx.send(embed=embed)
        else:
            added = []
            removed = []
            for role in roles:
                if role.id in self.bot.cache[ctx.guild.id]['settings']['admin_roles']:
                    self.bot.cache[ctx.guild.id]['settings']['admin_roles'].remove(role.id)
                    removed.append(f"- {role.name}")
                else:
                    self.bot.cache[ctx.guild.id]['settings']['admin_roles'].append(role.id)
                    added.append(f"+ {role.name}")

            if not added:
                added.append("+ No roles added!")
            if not removed:
                removed.append("- No roles removed")

            added_list = "```patch\n"
            for role in added:
                added_list += f"{role}\n"
            added_list += "```"
            removed_list = "```patch\n"
            for role in removed:
                removed_list += f"{role}\n"
            removed_list += "```"

            current = []
            for role in self.bot.cache[ctx.guild.id]['settings']['admin_roles']:
                cur = ctx.guild.get_role(role)
                current.append(cur.name)
            if not current:
                current.append("No configured roles.")

            embed = discord.Embed(title=f"{ctx.guild.name} Admin Role List", description='The following is a summary of what roles you just added, removed, and the current list of allowed roles.', color=self.bot.success_color)
            embed.add_field(name="ADDED", value=added_list, inline=False)
            embed.add_field(name="REMOVED", value=removed_list, inline=False)
            embed.add_field(name="CURRENT LIST", value=" | ".join(current), inline=False)
            await ctx.send(embed=embed)
        await self.bot.write_db(ctx.guild)

    @update_aroles.error
    async def ar_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            error_str = str(error)
            role_name = error_str[6:-12]
            message_list = ctx.message.content.split(' ')
            arg_list = message_list[1:]
            good_roles = []
            for arg in arg_list:
                good_roles.append(discord.utils.find(lambda r :  r.id == arg or r.name == arg or r.mention == arg, ctx.guild.roles))
            good_roles = [i for i in good_roles if i]
            if not good_roles:
                await ctx.send("ran out")


    @commands.command(name="bypass", aliases=['tbypass'], description='Toggle if admin roles can bypass cooldown or not.')
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def update_bypass(self, ctx):
        """Toggle the ability to allow admin roles to bypass the cooldown."""
        self.bot.cache[ctx.guild.id]['settings']['admin_bypass'] = not self.bot.cache[ctx.guild.id]['settings']['admin_bypass']
        embed=discord.Embed(title="Guild settings updated", description=f"You have changed the **admin bypass** flag for this guild.\nThe current value is: `{self.bot.cache[ctx.guild.id]['settings']['admin_bypass']}`", color=self.bot.success_color)
        embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f"A True value means defined admin roles are able to bypass the cooldown. A False value means they cannot bypass the cooldown.")
        await self.bot.write_db(ctx.guild)
        await ctx.send(embed=embed)       

    @commands.command(name='clean', aliases=['tclean'], description='Toggles the flag that controls if the bot should delete messages used to setup threads.')
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def update_cleaning(self, ctx):
        """Why you would change this is beyond me. Determines if the bot should delete messages used to create threads."""
        self.bot.cache[ctx.guild.id]['settings']['cleanup'] = not self.bot.cache[ctx.guild.id]['settings']['cleanup']
        embed=discord.Embed(title="Guild settings updated", description=f"You have changed the **cleanup** flag for this guild.\nThe current value is: `{self.bot.cache[ctx.guild.id]['settings']['cleanup']}`", color=self.bot.success_color)
        embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f"A True value means commands used to make threads will be deleted when possible. A False value means all messages used to create threads are kept.")
        await self.bot.write_db(ctx.guild)
        await ctx.send(embed=embed)       

def setup(bot):
    bot.add_cog(TB_Settings(bot))
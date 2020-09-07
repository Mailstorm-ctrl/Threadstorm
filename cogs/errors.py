import discord
import traceback
import random
import string
from time import gmtime, strftime
from datetime import datetime
from discord.ext import commands

class TB_errors(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    async def error_db(self, error_code, error_type):
        print(error_code)
        print(error_type)
        #async with self.bot.db.acquire() as con:
        #    await con.execute('INSERT INTO errors(error_code, error_type, date) VALUES ($1, $2, $3);', error_code, error_type, datetime.utcnow())

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.NoPrivateMessage):
            embed=discord.Embed(title="Command not DM-able", description=f"The command: `{ctx.prefix}{ctx.invoked_with}` cannot be ran in a private message.", color=self.bot.error_color)
            embed.set_author(name= ctx.bot.user.name, url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=ctx.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.BadUnionArgument):
            embed=discord.Embed(title="Failed to convert an argument!", description=f"{ctx.author.mention}, something hapened with your command.\nThe parameter: {error.param.name} failed to convert.\nThe converter(s): {error.converters} failed.", color=self.bot.error_color)
            embed.set_author(name=ctx.bot.user.name, url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=ctx.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            embed=discord.Embed(title="Missing argument!", description=f"{ctx.author.mention}, it appears you forgot to specify the {error.param.name} parameter. Please do so next time.", color=self.bot.error_color)
            embed.set_author(name=ctx.bot.user.name, url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=ctx.bot.user.avatar_url)
            await ctx.send(f"There's a missing argument here.")
            return
        elif isinstance(error, commands.CommandOnCooldown):
            # Bypass cooldown if allowed
            if any(item in [role.id for role in ctx.author.roles] for item in ctx.bot.cache[ctx.guild.id]['settings']["admin_roles"]) and ctx.bot.cache[ctx.guild.id]['settings']['admin_bypass']:
                await ctx.reinvoke(restart=True)
                return
            embed=discord.Embed(title="You're on cooldown!", description=f"{ctx.author.mention}, you are currently on cooldown.\nTry again in: {strftime('%H Hours and %M minutes.', gmtime(error.retry_after))}", color=self.bot.error_color)
            embed.set_author(name=ctx.bot.user.name, url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=ctx.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.MissingPermissions):
            embed=discord.Embed(title="Missing permissions!", description=f"{ctx.author.mention}, it appears *you* don't have permission to run this command.\nYou need permission(s):\n{', '.join(error.missing_perms)}", color=self.bot.error_color)
            embed.set_author(name=ctx.bot.user.name, url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=ctx.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.BotMissingPermissions):
            embed=discord.Embed(title="Missing permissions!", description=f"{ctx.author.mention}, I'm missing the permissions needed to run this command.\nI need the permission(s):\n{', '.join(error.missing_perms)}", color=self.bot.error_color)
            embed.set_author(name=ctx.bot.user.name, url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=ctx.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.CheckFailure):
            embed=discord.Embed(title="Check failure!", description=f"{ctx.author.mention}, the command: `{ctx.prefix}{ctx.invoked_with}` failed to execute. Possible causes:\nMissing required permission\n\nTrying to execute in a channel I don't manage", color=self.bot.error_color)
            embed.set_author(name=ctx.bot.user.name, url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=ctx.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return
        else:
            error_code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
            traceback_str = traceback.format_exception(type(error), error, error.__traceback__)
            new_trace = traceback_str[0]
            for line in traceback_str[1:]:
                new_trace += line.replace('\\n', '\n')
            embed=discord.Embed(title=f"Oh no! You (probably didn't) break it!", description=f'Here is the traceback:```python\n{new_trace}```\n\nHere is context info:```Author = {ctx.author.id}\nChannel = {ctx.channel.id}\nGuild = {ctx.guild.id}\nCommand = {ctx.message.content}```', color=self.bot.error_color)
            embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url, url="https://github.com/Mailstorm-ctrl/Threadstorm")
            embed.set_footer(text=f"Reportable error code: {error_code}")
            try:
                await ctx.send(embed=embed)
            except:
                await ctx.send(f"A generic error as occured. However, I'm unable to post a traceback. If you'd like to report this, please include this in your error report:\n{error_code}\n\nHere is context info:```Author = {ctx.author.id}\nChannel = {ctx.channel.id}\nGuild = {ctx.guild.id}\nCommand = {ctx.message.content}```")
            await self.error_db(error_code, traceback.format_exc())
            print(error)
            return
def setup(bot):
    bot.add_cog(TB_errors(bot))

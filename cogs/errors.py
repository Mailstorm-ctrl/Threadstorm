import discord
from time import gmtime
from time import strftime
from cogs.embeds import TB_Embeds
from discord.ext import commands

ERROR_COLOR = 0xf0ff67

class TB_errors(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.NoPrivateMessage):
            embed=discord.Embed(title="Command not DM-able", description=f"The command: `{ctx.prefix}{ctx.invoked_with}` cannot be ran in a private message.", color=ERROR_COLOR)
            embed.set_author(name= ctx.bot.user.name, url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=ctx.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.BadUnionArgument):
            embed=discord.Embed(title="Failed to convert an argument!", description=f"{ctx.author.mention}, something hapened with your command.\nThe parameter: {error.param.name} failed to convert.\nThe converter(s): {error.converters} failed.", color=ERROR_COLOR)
            embed.set_author(name=ctx.bot.user.name, url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=ctx.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            embed=discord.Embed(title="Missing argument!", description=f"{ctx.author.mention}, it appears you forgot to specify the {error.param.name} parameter. Please do so next time.", color=ERROR_COLOR)
            embed.set_author(name=ctx.bot.user.name, url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=ctx.bot.user.avatar_url)
            await ctx.send(f"There's a missing argument here.")
            return
        elif isinstance(error, commands.CommandOnCooldown):
            embed=discord.Embed(title="You're on cooldown!", description=f"{ctx.author.mention}, you are currently on cooldown.\nTry again in: {strftime('%H Hours and %M minutes.', gmtime(error.retry_after))}", color=ERROR_COLOR)
            embed.set_author(name=ctx.bot.user.name, url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=ctx.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.MissingPermissions):
            embed=discord.Embed(title="Missing permissions!", description=f"{ctx.author.mention}, it appears *you* don't have permission to run this command.\nYou need permission(s):\n{error.missing_perms}", color=ERROR_COLOR)
            embed.set_author(name=ctx.bot.user.name, url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=ctx.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.BotMissingPermissions):
            embed=discord.Embed(title="Missing permissions!", description=f"{ctx.author.mention}, I'm missing the permissions needed to run this command.\nI need the permission(s):\n{error.missing_perms}", color=ERROR_COLOR)
            embed.set_author(name=ctx.bot.user.name, url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=ctx.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.CheckFailure):
            embed=discord.Embed(title="Check failure!", description=f"{ctx.author.mention}, the command: `{ctx.prefix}{ctx.invoked_with}` can only be used in a channel that *I* created.", color=ERROR_COLOR)
            embed.set_author(name=ctx.bot.user.name, url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=ctx.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return
        else:
            embed = await TB_Embeds.oh_no_error(ctx, error)
            await ctx.send(embed=embed)
            return

def setup(bot):
    bot.add_cog(TB_errors(bot))
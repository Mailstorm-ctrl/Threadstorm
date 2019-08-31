import discord
from discord.ext import commands

class TB_Config(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cprefix', aliases=['tb_prefix'])
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, new_prefix):
        # update database with new prefix
        await ctx.send(f"Prefix updated to: {new_prefix}")

def setup(bot):
    bot.add_cog(TB_Config(bot))
import discord
from cogs.embeds import TB_Embeds
from discord.ext import commands

class TB_Checks():

    async def check_if_thread(ctx):
        try:
            if ctx.channel.id in ctx.bot.thread_check_cache.get(ctx.guild.id):
                return True
            else:
                return False
        except:
            return False
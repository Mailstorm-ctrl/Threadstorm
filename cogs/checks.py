import discord
import json
from cogs.embeds import TB_Embeds
from database.database import database
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

    async def check_if_category(ctx):
        sql = database(ctx.bot.db)
        custom_categories = await sql.get_custom_categories(ctx.guild)
        if custom_categories[0] is not None:
            try:
                custom_categories = json.loads(custom_categories[0])
            except:
                return False
            if ctx.channel.category.id in custom_categories.get(str(ctx.guild.id)):
                return True
            else:
                return False
        else:
            return False
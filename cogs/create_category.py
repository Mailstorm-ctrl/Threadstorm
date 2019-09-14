import discord
import json
import asyncio
from database.database import database
from cogs.embeds import TB_Embeds
from discord.ext import commands

class TB_Category_Creation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ccategory', aliases=['tcreate'])
    @commands.has_permissions(manage_channels=True)
    async def create_category(self, ctx, *, category):
        category = f'{category[:96]}...'
        thread_category = await ctx.guild.create_category(category, overwrites=ctx.channel.overwrites)
        custom_category_hub_channel = await ctx.guild.create_text_channel(f'Create threads here!', category=thread_category)
        sql = database(self.bot.db)
        custom_categories = await sql.get_custom_categories(ctx.guild)
        if custom_categories[0] is not None:
            custom_categories = json.loads(custom_categories[0])
            custom_categories[str(ctx.guild.id)].append(thread_category.id)
        else:
            custom_categories = {}
            custom_categories[ctx.guild.id] = [thread_category.id]
        await sql.update_custom_categories(json.dumps(custom_categories), ctx.guild)
        embed1 = await TB_Embeds.hub_channel(ctx, category)
        embed2 = await TB_Embeds.category_made(ctx, custom_category_hub_channel)
        pin_this = await custom_category_hub_channel.send(embed=embed1)
        await pin_this.pin()
        await ctx.send(embed=embed2)
        
    @commands.command(name='dcategory', aliases=['tdelete_category', 'tdc'])
    @commands.has_permissions(manage_guild=True)
    async def delete_category(self, ctx):
        sql = database(self.bot.db)
        default = True
        custom_category_check = await sql.get_custom_categories(ctx.guild)
        custom_category_check = json.loads(custom_category_check[0])
        if ctx.channel.category.id in custom_category_check.get(str(ctx.guild.id)):
            default = False
        if default:
            await ctx.send("This command cannot be ran in this channel. \
                It can only be ran in channels that belong to a category that I have made and isn't the default channel.")
            return
        else:
            await ctx.send(f"""Are you sure? This will delete the category and __***ALL***__ channels that belong to this category.
                            To confirm, please paste in the categorys ID:\n{ctx.channel.category.id}""")
            try:
                confirm = await self.bot.wait_for('message',
                                                check=lambda m : m.author.id == ctx.author.id and int(m.content) in custom_category_check.get(str(ctx.guild.id)),
                                                timeout=30
                                                )
            except asyncio.TimeoutError:
                await ctx.send("Timeout reached. No action has been taken.")
                return
            else:
                for channel in ctx.channel.category.channels:
                    await channel.delete(reason='PURGE CATEGORY')
                    await sql.delete_threads(channel)
                await ctx.channel.category.delete(reason='PURGE CATEGORY')
                custom_categories = await sql.get_custom_categories(ctx.guild)
                custom_categories = json.loads(custom_categories[0])
                custom_categories[str(ctx.guild.id)].remove(ctx.channel.category.id)
                await sql.update_custom_categories(custom_categories, json.dumps(custom_categories))

def setup(bot):
    bot.add_cog(TB_Category_Creation(bot))

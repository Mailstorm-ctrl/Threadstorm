import discord
import asyncio
from discord.ext import commands

class TB_Category_Creation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ccategory', aliases=['tcreate'], description='Create a custom category for the server')
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    async def create_category(self, ctx, *, category_name):
        category = f'{category_name[:96]}...'
        thread_category = await ctx.guild.create_category(category, overwrites=ctx.channel.overwrites)
        custom_category_hub_channel = await ctx.guild.create_text_channel(f'Create threads here!', category=thread_category)
        self.bot.cache[ctx.guild.id]["custom_categories"][thread_category.id] = custom_category_hub_channel.id
        
        hub_channel_embed = discord.Embed(title="THREAD HUB CHANNEL", description=f'Please create threads for the category `{category_name[:96]}` here.', color=self.bot.DEFAULT_COLOR)
        hub_channel_embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)

        confirmation = discord.Embed(title="Category created!", description=f'Please use {custom_category_hub_channel.mention} to place threads into this category. I\'ve left a reminder in there too.', color=self.bot.DEFAULT_COLOR)
        confirmation.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        confirmation.set_footer(text='You can rename this channel to whatever you wish. You can also move the category around.')

        pin_this = await custom_category_hub_channel.send(embed=hub_channel_embed)
        await pin_this.pin()
        await ctx.send(embed=confirmation)
        await self.bot.write_db(ctx.guild)
    
    @commands.command(name='dcategory', aliases=['tdelete_category', 'tdc'], description='Delete a custom category')
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    async def delete_category(self, ctx):
        """This command will wipe out a custom category. Meaning all threads will be deleted. Will need to verify before any action is taken."""
        category = ctx.channel.category
        error_msg = "This command cannot be ran here. Sorry. Please run it in a channel that is a part of one of your custom categories."
        if category is None:
            await ctx.send(error_msg)
            return
        if category.id not in self.bot.cache[ctx.guild.id]["custom_categories"]:
            await ctx.send(error_msg)
            return

        confirm = await ctx.send(f"Are you sure you want to do this? This will delete `{ctx.channel.category.name}` and __***ALL***__ channels that belong to `{ctx.channel.category.name}` ***(Even channels I did not make!)***.\nTo confirm this action, please react with the appropriate reaction.")
        await confirm.add_reaction('✔️')
        def check(reaction, user):
            return str(reaction.emoji) == '✔️' and reaction.message == confirm and user == ctx.author and reaction.message.channel.category.id in self.bot.cache[ctx.guild.id]["custom_categories"]
        try:
            react, user = await self.bot.wait_for('reaction_add', check=check, timeout=60)
        except asynio.TimeoutError:
            await ctx.send("Timeout reached. This action times out after 60 seconds.")
            return
        else:
            for channel in ctx.channel.category.channels:
                await channel.delete(reason='PURGE CATEGORY')
                self.bot.cache[ctx.guild.id]['active_threads'].pop(channel.id, None)
            self.bot.cache[ctx.guild.id]["custom_categories"].pop(ctx.channel.category.id, None)
            await self.bot.write_db(ctx.guild)

def setup(bot):
    bot.add_cog(TB_Category_Creation(bot))

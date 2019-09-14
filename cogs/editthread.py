import discord
import typing
from database.database import database
from cogs.embeds import TB_Embeds
from discord.ext import commands

class TB_Edit_Threads(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def is_thread(ctx):
        if ctx.channel.id in ctx.bot.thread_check_cache.get(ctx.guild.id):
            return True
        else:
            return False


    @commands.command(name='keep', aliases=['tkeep'])
    @commands.has_permissions(manage_channels=True)
    @commands.check(is_thread)
    async def keep(self, ctx):
        sql = database(self.bot.db)
        setting = await sql.get_thread_info_by_channel_id(ctx.channel)
        if setting[0][6]:
            await sql.update_keep_thread(ctx.channel, False)
            embed = await TB_Embeds.keep_thread(ctx, False)
        if not setting[0][6]:
            await sql.update_keep_thread(ctx.channel, True)
            embed = await TB_Embeds.keep_thread(ctx, True)
        await ctx.send(embed=embed)
        

    @commands.command(name='edit', aliases=['tedit'])
    @commands.check(is_thread)
    async def thread_edit(self, ctx, part: str, *, text: typing.Optional[str] = 'Blank'):
        """Lets guild moderators and the owner of the thread edit/append to the original post."""
        if ctx.guild is None:
            await ctx.send("You cannot use this command in a DM.")
            return
        part = part.lower()
        sql = database(self.bot.db)
        thread_info = await sql.get_thread_info_by_channel_id(ctx.channel)
        thread_info = thread_info[0]
        
        #Index 5 is the "author" of the thread.
        if thread_info[5] is None:
            await ctx.send("Unable to get thread author. Cannot continue.")
            return

        if thread_info[5] != ctx.author.id and not ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.send("You are not the author of this thread. You do not have permission to edit this.")
            return

        if part not in ['title','body', 'image']:
            await ctx.send(
                "You may only edit the `title` or `body` of this thread. When editing the body, \
                new text is appended and an 'EDIT' tag is added to the message."
                )
            return

        if part == 'image':
            if len(ctx.message.attachments) > 0:
                text = ctx.message.attachments[0].url
                
        Thread_OP = await ctx.channel.fetch_message(thread_info[3])
        Thread_OP_Embed = Thread_OP.embeds[0]
        TOE_Title = Thread_OP_Embed.title
        TOE_Body = Thread_OP_Embed.description
        TOE_Color = Thread_OP_Embed.color
        TOE_Author = Thread_OP_Embed.author
        TOE_Image = Thread_OP_Embed.image.url

        if thread_info[5] != ctx.author.id and ctx.channel.permissions_for(ctx.author).manage_messages:
            embed = await TB_Embeds.thread_edit_mod(part, text, ctx.author, TOE_Body, TOE_Title, TOE_Color, TOE_Author, TOE_Image)
            if len(embed) >= 2046:
                await ctx.send("I cannot modify this threads OP. The message will exceed discords max length limit.")
                return
            if part == 'title':
                await ctx.channel.edit(name=text[:96]+'...')
            await Thread_OP.edit(embed=embed)
            mod_edit = await TB_Embeds.thread_edit_mod_announcment(ctx.author, part)
            await ctx.send(embed=mod_edit)

        if thread_info[5] == ctx.author.id:
            embed = await TB_Embeds.thread_edit_nm(part, text, TOE_Body, TOE_Title, TOE_Color, TOE_Author, TOE_Image)
            if len(embed.description) >= 2046:
                await ctx.send("I cannot modify this threads OP. The message will exceed discords max length limit.")
                return
            if part == 'title':
                await ctx.channel.edit(name=text[:96]+'...')
            await Thread_OP.edit(embed=embed)
            user_edit = await TB_Embeds.thread_edit_announcment(ctx.author, part)
            await ctx.send(embed=user_edit)

def setup(bot):
    bot.add_cog(TB_Edit_Threads(bot))

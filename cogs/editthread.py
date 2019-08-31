import discord
import typing
from database.database import database
from cogs.embeds import TB_Embeds
from discord.ext import commands

class TB_Edit_Threads(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='edit', aliases=['tedit'])
    async def thread_edit(self, ctx, part: str, *, text):
        if ctx.guild is None:
            await ctx.send("You cannot use this command in a DM.")
            return
        part = part.lower()
        sql = database(self.bot.db)
        thread_id = await sql.get_thread_id_from_channel(ctx.channel)
        thread_id = thread_id[0]
        thread_info = self.bot.all_channels.get(thread_id)

        if thread_info[3] is None:
            await ctx.send("Unable to get thread author. Cannot continue.")
            return

        if thread_info[3] != ctx.author.id and not ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.send("You are not the author of this thread. You do not have permission to edit this.")
            return

        if part not in ['title','body']:
            await ctx.send("You may only edit the `title` or `body` of this thread. When editing the body, new text is appended and an 'EDIT' tag is added to the message.")
            return

        Thread_OP = await ctx.channel.fetch_message(self.bot.all_channels.get(thread_id)[2])
        Thread_OP_Embed = Thread_OP.embeds[0]
        TOE_Title = Thread_OP_Embed.title
        TOE_Body = Thread_OP_Embed.description
        TOE_Color = Thread_OP_Embed.color
        TOE_Author = Thread_OP_Embed.author

        if thread_info[3] != ctx.author.id and ctx.channel.permissions_for(ctx.author).manage_messages:
            embed = await TB_Embeds.thread_edit_mod(part, text, ctx.author, TOE_Body, TOE_Title, TOE_Color, TOE_Author)
            if part == 'title':
                await ctx.channel.edit(name=text[:17])
            await Thread_OP.edit(embed=embed)
            mod_edit = await TB_Embeds.thread_edit_mod_announcment(ctx.author, part)
            await ctx.send(embed=mod_edit)

        if thread_info[3] == ctx.author.id:
            embed = await TB_Embeds.thread_edit_nm(part, text, TOE_Body, TOE_Title, TOE_Color, TOE_Author)
            if part == 'title':
                await ctx.channel.edit(name=text[:17])
            await Thread_OP.edit(embed=embed)
            user_edit = await TB_Embeds.thread_edit_announcment(ctx.author, part)
            await ctx.send(embed=user_edit)

def setup(bot):
    bot.add_cog(TB_Edit_Threads(bot))
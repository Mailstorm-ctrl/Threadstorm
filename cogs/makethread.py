import discord
import asyncio
import typing
import json
from database.database import database
from cogs.embeds import TB_Embeds
from cogs.checks import TB_Checks
from discord.ext import commands


class TB_Thread_Creation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='makethread',aliases=['tmake'], description='Make a new thread')
    @commands.cooldown(2, 7200,type=commands.BucketType.member)
    @commands.bot_has_permissions(manage_messages=True, manage_channels=True)
    @commands.guild_only()
    async def manual_create(self, ctx):
        """Pretty simple really. Server members can make their own threads. Run the command and then follow the directions"""

        if ctx.guild is None:
            return

        channel_permissions = ctx.channel.overwrites

        sql = database(self.bot.db)
        get_chan = await sql.get_thread_category_id(ctx.guild)
        try:
            thread_category = ctx.guild.get_channel(get_chan[0])
        except IndexError:
            await ctx.send(f"It seems your guild is not located in the database. Please run: `{ctx.prefix}tsetup`\nMake sure I'm allowed to manage channels, messages, and roles before running this!")
            return
        abort = None
        thread = {}
        step = 1
        keep_channel_clean = {ctx.author.id: [ctx.message.id]}

        while 1:
            if abort == 'abort' or step > 2:
                break
            embed = await TB_Embeds.make_thread(ctx, step)
            question = await ctx.send(embed=embed)
            try:
                text = await self.bot.wait_for('message', check=lambda m : m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=900)
            except asyncio.TimeoutError:
                await ctx.send("Thread creation aborted. Timeout has been reached.")
                return
            else:
                keep_channel_clean[ctx.author.id].extend([text.id, question.id])
                abort = text.content
                thread[step] = text.content
                step += 1
        default = True
        custom_category_check = await sql.get_custom_categories(ctx.guild)
        try:
            custom_category_check = json.loads(custom_category_check[0])
            if ctx.channel.category.id in custom_category_check.get(str(ctx.guild.id)):
                default = False
        except:
            pass

        if abort == 'abort':
            if not default:
                loop_amount = len(keep_channel_clean.get(ctx.author.id))
                async for message in ctx.channel.history():
                    if loop_amount == 0:
                        break
                    if message.id in keep_channel_clean.get(ctx.author.id):
                        await message.delete()
                        loop_amount -= 1
            else:
                await ctx.send("Thread creation aborted. You provoked this.")
            return

        thread_embed = await TB_Embeds.manual_creation(ctx, thread)
        if default:
            thread_channel = await ctx.guild.create_text_channel(f'{thread.get(1)[:96]}...', overwrites=channel_permissions, category=thread_category, reason=f'{ctx.author} created this thread.', topic=f'{thread.get(2)[:1019]}...')
        else:
            thread_channel = await ctx.guild.create_text_channel(f'{thread.get(1)[:96]}...', category=ctx.channel.category, position=len(ctx.channel.category.text_channels)-1, topic=f'{thread.get(2)[:1019]}...')      
            await ctx.channel.edit(position=0)
        await sql.create_thread(thread_channel, ctx.author, ctx.message)
        thread_info = await sql.get_thread_info_by_channel_id(thread_channel)
        thread_op = await thread_channel.send(embed=thread_embed)
        created = await TB_Embeds.thread_created(thread_channel)
        await thread_op.pin()
        await sql.update_thread_op(thread_channel,thread_op)

        if not default:
            loop_amount = len(keep_channel_clean.get(ctx.author.id))
            async for message in ctx.channel.history():
                if loop_amount == 0:
                    break
                if message.id in keep_channel_clean.get(ctx.author.id):
                    await message.delete()
                    loop_amount -= 1
        else:
            await ctx.send(embed=created)
        try:
            self.bot.thread_check_cache[ctx.guild.id].append(thread_channel.id)
        except KeyError:
            self.bot.thread_check_cache[ctx.guild.id] = [thread_channel.id]


def setup(bot):
    bot.add_cog(TB_Thread_Creation(bot))

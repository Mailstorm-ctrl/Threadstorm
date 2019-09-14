import discord
import asyncio
import typing
import json
from database.database import database
from cogs.embeds import TB_Embeds
from discord.ext import commands


class TB_Thread_Creation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='makethread',aliases=['tmake'])
    @commands.cooldown(2, 7200,type=commands.BucketType.member)
    async def manual_create(self, ctx):
        """Lets members create their own threads. This command will put
        "threads" that aren't in a custom category into the general threads category the bot made when it joined the server.
        If the invoked command is in a category that was made with the bot, the created thread will appear in that category.
        This lets servers have organized threads."""

        if ctx.guild is None:
            return

        channel_permissions = ctx.channel.overwrites

        sql = database(self.bot.db)
        get_chan = await sql.get_thread_category_id(ctx.guild)
        thread_category = ctx.guild.get_channel(get_chan[0])
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
        custom_category_check = json.loads(custom_category_check[0])
        if ctx.channel.category.id in custom_category_check.get(str(ctx.guild.id)):
            default = False

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

import discord
import asyncio
import typing
from database.database import database
from cogs.embeds import TB_Embeds
from discord.ext import commands

class TB_Thread_Creation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Let's Talk About That", aliases=['ltat','tt', 'thread', 'threadthis'])
    async def create_thread(self, ctx, topic: typing.Optional[int] = 0):
        if ctx.guild is None:
            return

        channel_permissions = {}
        for role in ctx.guild.roles:
            channel_permissions[role] = ctx.channel.overwrites_for(role)
        thread_category = ctx.guild.get_channel(self.bot.thread_categories.get(ctx.guild.id))
        sql = database(self.bot.db)

        if topic != 0:
            msg = await ctx.channel.fetch_message(topic)

            if msg is None:
                await ctx.send("The message ID you supplied is either not in this channel or is not valid. Try again please.")
                return

            try:
                thread_channel = await ctx.guild.create_text_channel(msg.content[:17], overwrites=channel_permissions, category=thread_category, reason=f'{ctx.author} created this thread.')
                await sql.create_thread(thread_channel, ctx.author, msg)
                thread_id = await sql.get_thread_id_from_channel(thread_channel)
                await thread_channel.edit(topic=f'The ID of this thread is: {thread_id[0]}')
            except discord.Forbidden:
                await ctx.send("Channel creation failed. Maybe I'm lacking permissions?")
                await sql.delete_thread(thread_id[0])
                return

            op = await TB_Embeds.thread_op(msg)
            notify_msg_author = await TB_Embeds.thread_op_author(thread_channel, ctx.author, thread_id[0])
            created = await TB_Embeds.thread_created(thread_id[0])
            thread_op = await thread_channel.send(embed=op)
            await thread_op.pin()
            self.bot.all_channels[thread_id[0]] = [ctx.guild.id, thread_channel.id, thread_op.id, ctx.author.id, msg.author.id]
            await sql.update_thread_op(thread_id[0],thread_op)
            await msg.author.send(embed=notify_msg_author)
            await ctx.send(embed=created)
            return
        
        history_counter = 0
        possible_topics = {}

        async for message in ctx.channel.history():
            if history_counter >= 20:
                break
            message_length_bool = True if len(message.content) > 30 else False
            if not message.author.bot and message_length_bool and message.author.id != duplicate_author:
                possible_topics[history_counter] = [message.author.id, message.content[:len(message.content)%300]+'...', message.id]
                history_counter += 1
            
            #duplicate_author = message.author.id
            duplicate_author = 0

        embed = await TB_Embeds.potential_threads(possible_topics, self.bot)
        possible_topics[history_counter] = [None]
        await ctx.send(embed=embed)

        try:
            choice = await self.bot.wait_for('message', check=lambda m: ctx.author.id == m.author.id and ctx.channel.id == m.channel.id and m.content in str(possible_topics.keys()), timeout=120)
        except asyncio.TimeoutError:
           await ctx.send("Oh no, you didn't answer fast enough. Try again, but faster this time.")
           return
        else:
            if int(choice.content) == history_counter:
                await ctx.send("Please go mark the message you want to make a thread about. I'll be waiting.")

                try:
                    obj = await self.bot.wait_for('raw_reaction_add', check=lambda payload: ctx.author.id == payload.user_id and ctx.channel.id == payload.channel_id, timeout=120)
                except asyncio.TimeoutError:
                    await ctx.send("Timed out.")
                    return                    
                else:
                    msg = await ctx.channel.fetch_message(obj.message_id)             
                    try:
                        thread_channel = await ctx.guild.create_text_channel(msg.content[:len(msg.content)%17], overwrites=channel_permissions, category=thread_category, reason=f'{ctx.author} created this thread.')
                        await sql.create_thread(thread_channel, ctx.author, msg)
                        thread_id = await sql.get_thread_id_from_channel(thread_channel)
                        await thread_channel.edit(topic=f'The ID of this thread is: {thread_id[0]}')
                    except discord.Forbidden:
                        await ctx.send("Channel creation failed. Maybe I'm lacking permissions?")
                        await sql.delete_thread(thread_id[0])
                        return

                    op = await TB_Embeds.thread_op(msg)
                    notify_msg_author = await TB_Embeds.thread_op_author(thread_channel, ctx.author, thread_id[0])
                    created = await TB_Embeds.thread_created(thread_id[0])
                    thread_op = await thread_channel.send(embed=op)
                    await thread_op.pin()
                    self.bot.all_channels[thread_id[0]] = [ctx.guild.id, thread_channel.id, thread_op.id, ctx.author.id, msg.author.id]
                    await sql.update_thread_op(thread_id[0],thread_op)
                    await msg.author.send(embed=notify_msg_author)
                    await ctx.send(embed=created)
                    return

            else:
                msg = await ctx.channel.fetch_message(possible_topics.get(int(choice.content))[2])
                
                try:
                    thread_channel = await ctx.guild.create_text_channel(msg.content[:len(msg.content)%17], overwrites=channel_permissions, category=thread_category, reason=f'{ctx.author} created this thread.')
                    await sql.create_thread(thread_channel, ctx.author, msg)
                    thread_id = await sql.get_thread_id_from_channel(thread_channel)
                    await thread_channel.edit(topic=f'The ID of this thread is: {thread_id[0]}')
                except discord.Forbidden:
                    await ctx.send("Channel creation failed. Maybe I'm lacking permissions?")
                    await sql.delete_thread(thread_id[0])
                    return

                op = await TB_Embeds.thread_op(msg)
                notify_msg_author = await TB_Embeds.thread_op_author(thread_channel, ctx.author, thread_id[0])
                created = await TB_Embeds.thread_created(thread_id[0])
                thread_op = await thread_channel.send(embed=op)
                await thread_op.pin()
                self.bot.all_channels[thread_id[0]] = [ctx.guild.id, thread_channel.id, thread_op.id, ctx.author.id, msg.author.id]
                await sql.update_thread_op(thread_id[0],thread_op)
                await msg.author.send(embed=notify_msg_author)
                await ctx.send(embed=created)
                return

def setup(bot):
    bot.add_cog(TB_Thread_Creation(bot))
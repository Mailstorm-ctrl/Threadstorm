#import asyncpg
import time
import asyncio
from os.path import join, dirname
from dotenv import load_dotenv

#Role: Thread-bot
# U
# Need 2 tables
#
# GUILD_CONFIGURATION TABLE:
#
#     Guild_id, prefix, threads_category_id
#
# THREAD TABLE:
#
#     Thread_id (auto-increment int), guild_id, channel_id, op_message_id, created_by_id, thread_author_id, last_message_time

class database:

    def __init__(self, con):
        self.con = con

    async def joined_guild(self, guild, category):
        await self.con.execute(f"INSERT INTO guild_configuration(guild_id,prefix,threads_category_id) VALUES({guild.id},'!',{category.id});")
        return

    def get_prefix(self, guild):
        cur = self.con.cursor()
        cur.execute(f'SELECT prefix FROM guild_configuration WHERE guild_id={guild.id};')
        return cur.fetchone()

    async def update_prefix(self, guild, prefix):
        await self.con.execute(f"UPDATE guild_configuration SET prefix='{prefix}' WHERE guild_id={guild.id};")
        return

    async def set_threads_category_id(self, guild, cid):
        await self.con.execute(f'UPDATE guild_configuration SET threads_category_id={cid} WHERE guild_id={guild.id};')
        return

    async def create_thread(self, channel, author, msg):
        await self.con.execute(f'INSERT INTO threads (guild_id, channel_id, created_by, thread_author) VALUES({channel.guild.id},{channel.id},{author.id},{msg.author.id});')
        return True

    async def update_thread_op(self, thread_id, op_message):
        await self.con.execute(f'UPDATE threads SET op_message_id={op_message.id} WHERE thread_id={thread_id};')

    async def update_last_message(self, k, v):
        await self.con.execute(f'UPDATE threads SET last_message_time={v[1]} WHERE channel_id={k} AND guild_id={v[0]};')
        return

    async def delete_thread(self, thread_id):
        await self.con.execute(f'DELETE FROM threads WHERE thread_id={thread_id};')
        return

    async def get_all_threads(self):
        """Database query used to fill cache with all channel information for quicker lookups"""
        return {row[0]:[row[1],row[2],row[3],row[4],row[5],row[6]] for row in await self.con.fetch('SELECT * FROM threads;')}

    async def get_thread_category_ids(self):
        cats = {}
        q = await self.con.fetch(f'SELECT guild_id, threads_category_id FROM guild_configuration;')
        for row in q:
            cats[row[0]] = row[1]
        return cats

    async def get_thread_channels(self):
        return {row[0]:row[1] for row in await self.con.fetch('SELECT channel_id, guild_id FROM threads')}

    async def get_thread_id_from_channel(self, channel):
        return [row[0] for row in await self.con.fetch(f'SELECT thread_id FROM threads WHERE guild_id={channel.guild.id} AND channel_id={channel.id};')]

    async def get_last_messages(self):
        return {row[0]:[row[1], row[2]] for row in await self.con.fetch(f'SELECT channel_id,guild_id,last_message_time FROM threads;')}
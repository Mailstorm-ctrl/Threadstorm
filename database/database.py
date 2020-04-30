#import asyncpg
#import asyncio
import time

class database:

    def __init__(self, con):
        self.con = con

    async def joined_guild(self, guild, category):
        async with self.con.acquire() as con:
            await con.execute(f"INSERT INTO guild_configuration(guild_id, prefix, threads_category_id) VALUES($1, $2, $3) ON CONFLICT (guild_id) DO UPDATE SET threads_category_id=$3;", guild.id, '.', category.id)
    def get_prefix(self, guild):
        cur = self.con.cursor()
        cur.execute(f'SELECT prefix FROM guild_configuration WHERE guild_id=%s;', (guild.id,))
        return cur.fetchone()

    async def update_prefix(self, guild, prefix):
        async with self.con.acquire() as con:
            await con.execute(f"UPDATE guild_configuration SET prefix=$1 WHERE guild_id=$2;", prefix, guild.id)

    async def set_threads_category_id(self, guild, cid):
        async with self.con.acquire() as con:
            await con.execute(f'UPDATE guild_configuration SET threads_category_id=$1 WHERE guild_id=$2;', cid, guild.id)

    async def create_thread(self, channel, author, msg):
        async with self.con.acquire() as con:
            await con.execute(f'INSERT INTO threads (guild_id, channel_id, created_by, thread_author, keep_thread) VALUES($1, $2, $3, $4, $5);', channel.guild.id, channel.id, author.id, msg.author.id, False)

    async def update_custom_categories(self, categories, guild):
        async with self.con.acquire() as con:
            await con.execute('UPDATE guild_configuration SET custom_categories=$1::jsonb WHERE guild_id=$2', categories, guild.id)

    async def update_channel_permissions_by_channel(self, channel, permissions):
        async with self.con.acquire() as con:
            await con.execute(f"UPDATE threads SET permission_values=$1::jsonb WHERE channel_id=$2 AND guild_id=$3;", permissions, channel.id, channel.guild.id)

    async def update_thread_op(self, thread, op_message):
        async with self.con.acquire() as con:
            await con.execute(f'UPDATE threads SET op_message_id=$1 WHERE channel_id=$2 AND guild_id=$3;', op_message.id, thread.id, thread.guild.id)

    async def update_last_message(self, channel):
        async with self.con.acquire() as con:
            await con.execute(f"""UPDATE threads SET last_message_age=$1 WHERE channel_id=$2 AND guild_id=$3;""", round(time.time()), channel.id, channel.guild.id)

    async def update_keep_thread(self, channel, setting):
        async with self.con.acquire() as con:
            await con.execute("UPDATE threads SET keep_thread=$1 WHERE channel_id=$2 AND guild_id=$3;", setting, channel.id, channel.guild.id)

    async def delete_thread_old(self):
        async with self.con.acquire() as con:
            await con.execute("DELETE FROM threads WHERE last_message_age < (extract(epoch from now())-432000) AND keep_thread=FALSE;")

    async def delete_threads(self, thread):
        async with self.con.acquire() as con:
            await con.execute('DELETE FROM threads WHERE channel_id=$1 and guild_id=$2', thread.id, thread.guild.id)

    async def get_thread_info_by_channel_id(self, channel):
        async with self.con.acquire() as con:
            return [[row[0], row[1],row[2],row[3],row[4],row[5],row[6],row[7]] for row in await con.fetch(f'SELECT * FROM threads WHERE channel_id=$1 AND guild_id=$2;', channel.id, channel.guild.id)]
    
    async def get_permissions_for_channel(self, channel):
        async with self.con.acquire() as con:
            return [row[0] for row in await con.fetch(f'SELECT permission_values FROM threads WHERE channel_id=$1 AND guild_id=$2;', channel.id, channel.guild.id)]

    async def get_thread_category_id(self, guild):
        async with self.con.acquire() as con:
            return [row[0] for row in await con.fetch(f'SELECT threads_category_id FROM guild_configuration WHERE guild_id=$1;', guild.id)]

    async def get_custom_categories(self, guild):
        async with self.con.acquire() as con:
            return [row[0] for row in await con.fetch('SELECT custom_categories FROM guild_configuration WHERE guild_id=$1', guild.id)]

    async def get_thread_channels(self):
        async with self.con.acquire() as con:
            q = await con.fetch('SELECT DISTINCT guild_id FROM threads;')
            cache = {record[0]:[] for record in await con.fetch('SELECT DISTINCT guild_id FROM threads;')}
            for guild in cache:
                q = await con.fetch('SELECT channel_id FROM threads WHERE guild_id=$1;', guild)
                for channel in q:
                    cache[guild].append(channel[0])
            return cache

    async def get_all_thread_channels(self):
        async with self.con.acquire() as con:
            return len([record[0] for record in await con.fetch('SELECT thread_id FROM threads;')])

    async def get_guilds(self):
        async with self.con.acquire() as con:
            glist = [row[0] for row in await con.fetch('SELECT guild_id FROM guild_configuration;')]
            return glist

    async def get_full_dead_channels(self):
        async with self.con.acquire() as con:
            dlist = [row[0] for row in await con.fetch("SELECT channel_id FROM threads WHERE last_message_age < (extract(epoch from now())-345600) AND keep_thread=FALSE;")]
            return dlist

    async def get_half_dead_channels(self):
        async with self.con.acquire() as con:
            dlist = [row[0] for row in await con.fetch("SELECT channel_id FROM threads WHERE last_message_age < (extract(epoch from now())-259200) AND last_message_age > (extract(epoch from now())-345600) AND keep_thread = FALSE;")]
            return dlist
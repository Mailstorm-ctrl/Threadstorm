import discord
import typing
import asyncio
import json
from cogs.embeds import TB_Embeds
from cogs.checks import TB_Checks
from database.database import database
from discord.ext import commands

class TB_Lock_Threads(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def is_thread(ctx):
        if ctx.channel.id in ctx.bot.thread_check_cache.get(ctx.guild.id):
            return True
        else:
            return False

    @commands.command(name='lock',aliases=['tlock'], description='Lock a thread')
    @commands.has_permissions(manage_messages=True)
    @commands.check(TB_Checks.check_if_thread)
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    @commands.guild_only()
    async def lock_thread(self, ctx, *, reason: typing.Optional[str] = 'No reason provided.'):
        """This command will go through a threads permission tree and set the `send_message` permission to `Deny` unless a role/member has the `manage_message` permission."""
        thread_locked_embed = await TB_Embeds.thread_locked(ctx.author, reason)
        await ctx.send(embed=thread_locked_embed)
        sql = database(self.bot.db)
        thread_permissions = {role.id:[ctx.channel.overwrites.get(role).pair()[0].value, ctx.channel.overwrites.get(role).pair()[1].value] for role in ctx.channel.overwrites}
        if len(thread_permissions) == 0:
            await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        else:
            await sql.update_channel_permissions_by_channel(ctx.channel, json.dumps(thread_permissions))
            for role in ctx.channel.overwrites:
                if not role.permissions.manage_messages and role != ctx.guild.default_role:
                    await ctx.channel.set_permissions(role, send_messages=False, read_messages=True, reason=reason)
                else:
                    continue

    @commands.command(name='unlock',aliases=['tunlock'], description='Unlocks a thread')
    @commands.has_permissions(manage_messages=True)
    @commands.check(TB_Checks.check_if_thread)
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    @commands.guild_only()
    async def unlock_thread(self, ctx):
        """The opposite of lock. This will restore the permission structure to what it was when `lock` was invoked."""
        sql = database(self.bot.db)
        thread_permissions = await sql.get_permissions_for_channel(ctx.channel)
        try:
            thread_permissions = json.loads(thread_permissions[0])
        except TypeError:
            pass
        if None in thread_permissions:
            await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        else:
            for role_id in thread_permissions:
                role = ctx.guild.get_role(int(role_id))
                allow = discord.Permissions(permissions=thread_permissions.get(role_id)[0])
                deny = discord.Permissions(permissions=thread_permissions.get(role_id)[1])
                await ctx.channel.set_permissions(role, overwrite=discord.PermissionOverwrite().from_pair(allow,deny))
        embed = await TB_Embeds.thread_unlocked(ctx.author)
        await ctx.send(embed=embed)

    @commands.command(name='delete', aliases=['tdelete'], description='Delete a singular thread')
    @commands.check(TB_Checks.check_if_thread)
    @commands.guild_only()
    async def delete_thread(self, ctx):
        """A command that deletes a single thread. This command must be invoked within a thread and only the owner of the thread or members with the `manage_channels` permission can invoke this command."""
        sql = database(self.bot.db)
        thread_info = await sql.get_thread_info_by_channel_id(ctx.channel)
        thread_info = thread_info[0]
        if ctx.author.id == thread_info[5]:
            await ctx.channel.delete()
        elif ctx.author.permissions_in(ctx.channel).manage_channels:
            await ctx.channel.delete()
        else:
            await ctx.send('You do not own this thread or do not have permission to delete channels.')

def setup(bot):
    bot.add_cog(TB_Lock_Threads(bot))

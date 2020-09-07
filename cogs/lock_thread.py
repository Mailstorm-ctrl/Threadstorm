import discord
import typing
from discord.ext import commands
from datetime import datetime

class TB_Thread_Locking(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def if_thread(ctx):
        return ctx.channel.id in ctx.bot.cache[ctx.guild.id]['active_threads']

    @commands.command(name='lock', aliases=['tlock'], description='Lock a thread')
    @commands.has_permissions(manage_channels=True, manage_roles=True)
    @commands.guild_only()
    @commands.check(if_thread)
    async def lock_thread(self, ctx, reason: typing.Optional[str] = "No reason provided"):
        if isinstance(ctx, discord.TextChannel):
            # Strictly used for the channel checker. ctx will never be a channel object except in this instance
            channel = ctx
            author = self.bot.user
        else:
            channel = ctx.channel
            author = ctx.author
        self.bot.cache[ctx.guild.id]['active_threads'][channel.id]['permissions'] = {obj.id:[channel.overwrites.get(obj).pair()[0].value, channel.overwrites.get(obj).pair()[1].value] for obj in channel.overwrites}
        if len(self.bot.cache[ctx.guild.id]['active_threads'][channel.id]['permissions']) == 0:
            await channel.set_permissions(ctx.guild.me, send_messages=True)
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        else:
            ow = ctx.channel.overwrites

            for obj,value in ow.items():
                if isinstance(obj, discord.Member):
                    if (not obj.permissions_in(channel).manage_messages or not obj.permissions_in(channel).manage_channels) and obj != ctx.guild.me:
                        value.update(send_messages=False)
                else:
                    if (not obj.permissions.manage_messages or not obj.permissions.manage_channels) and obj != ctx.guild.me:
                        value.update(send_messages=False)
                                 
            await ctx.channel.edit(overwrites=ow)
            await channel.set_permissions(ctx.guild.me, send_messages=True)
        embed=discord.Embed(title=":lock: THREAD LOCKED :lock:", description=f"This thread has been **__locked__**!\nResponsible Moderator: **{author.name}**\nReason for lock: **{reason}**", color=self.bot.warning_color)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f"Thread locked on: {datetime.now().strftime('%B %d at %H:%M')}")
        await ctx.send(embed=embed)
    
    @commands.command(name='unlock',aliases=['tunlock'], description='Unlocks a thread')
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    @commands.guild_only()
    @commands.check(if_thread)
    async def unlock_thread(self, ctx):
        """The opposite of lock. This will restore the permission structure to what it was when `lock` was invoked."""
        permissions = self.bot.cache[ctx.guild.id]['active_threads'][ctx.channel.id]['permissions']
        if len(permissions) == 0:
            overwrite = discord.PermissionsOverwrite()
            overwrite.send_messages = None
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        else:
            ow = {}
            for obj_id in permissions:
                obj = ctx.guild.get_role(int(obj_id))
                if obj is None:
                    obj = ctx.guild.get_member(obj_id)
                allow = discord.Permissions(permissions=permissions.get(obj_id)[0])
                deny = discord.Permissions(permissions=permissions.get(obj_id)[1])
                ow[obj] = discord.PermissionOverwrite().from_pair(allow,deny)
                #await ctx.channel.set_permissions(obj, overwrite=discord.PermissionOverwrite().from_pair(allow,deny))
            await ctx.channel.edit(overwrites=ow)
        embed=discord.Embed(title=":unlock: THREAD UNLOCKED :unlock:", description=f"This thread is now **__unlocked__**!\nResponsible Moderator: **{ctx.author.name}**", color=self.bot.success_color)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f"Thread unlocked on: {datetime.now().strftime('%B %d at %H:%M')}")
        await ctx.send(embed=embed)

    @commands.command(name='delete', aliases=['tdelete'], description='Delete a singular thread')
    @commands.guild_only()
    @commands.check(if_thread)
    async def delete_thread(self, ctx):
        """A command that deletes a single thread. This command must be invoked within a thread and only the owner of the thread or members with the `manage_channels` permission can invoke this command."""
        if ctx.author.id == self.bot.cache[ctx.guild.id]['active_threads'][ctx.channel.id]['author_id']:
            await ctx.channel.delete()
            self.bot.cache[ctx.guild.id]['active_threads'].pop(ctx.channel.id, None)
        elif ctx.author.permissions_in(ctx.channel).manage_channels:
            await ctx.channel.delete()
            self.bot.cache[ctx.guild.id]['active_threads'].pop(ctx.channel.id, None)
        else:
            await ctx.send('You do not own this thread or do not have permission to delete channels.')
            return
        await self.bot.write_db(ctx.guild)

def setup(bot):
    bot.add_cog(TB_Thread_Locking(bot))

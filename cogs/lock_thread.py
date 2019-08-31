import discord
import typing
from cogs.embeds import TB_Embeds
from discord.ext import commands

class TB_Lock_Threads(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='lock',aliases=['tlock'])
    @commands.has_permissions(manage_messages=True)
    async def lock_thread(self, ctx, *, reason: typing.Optional[str] = 'No reason provided.'):
        thread_locked_embed = await TB_Embeds.thread_locked(ctx.author, reason)
        await ctx.send(embed=thread_locked_embed)
        for role in ctx.guild.roles:
            if not role.permissions.manage_messages:
                await ctx.channel.set_permissions(role, send_messages=False, reason=reason)
            else:
                continue

    @commands.command(name='unlock',aliases=['tunlock'])
    @commands.has_permissions(manage_messages=True)
    async def unlock_thread(self, ctx):
        await ctx.send('WIP!')

    @commands.command(name='delete', aliases=['tdelete'])
    async def delete_thread(self, ctx):
        if ctx.author.id == self.bot.all_channels.get(thread_id)[4]:
            await ctx.channel.delete()
        else:
            if ctx.author.permissions.manage_channels:
                await ctx.channel.delete()

def setup(bot):
    bot.add_cog(TB_Lock_Threads(bot))
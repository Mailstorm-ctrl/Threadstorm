import discord
import traceback
from datetime import datetime
from discord.ext import commands

DEFAULT_COLOR = 0x69dce3
THREAD_STATE_CHANGE = 0xe4a501
ERROR_COLOR = 0xf0ff67

class TB_Embeds(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def oh_no_error(ctx, error):
        traceback_str = traceback.format_exception(type(error), error, error.__traceback__)
        new_trace = traceback_str[0]
        for line in traceback_str[1:]:
            new_trace += line.replace('\\n', '\n')
        embed=discord.Embed(title=f"Oh no! You (probably didn't) break it!", description=f'Here is the traceback:```python\n{new_trace}```\n\nHere is context info:```Author = {ctx.author.id}\nChannel = {ctx.channel.id}\nGuild = {ctx.guild.id}\nCommand = {ctx.message.content}```', color=ERROR_COLOR)
        embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
        return embed

    async def thread_created(thread):
        embed=discord.Embed(title="Success!", description=f"Your requested thread was made! It can be found at: {thread.mention}", color=DEFAULT_COLOR)
        embed.set_footer(text='This thread has the same permissions as this channel does.')
        return embed

    async def thread_edit_nm(part, text, TOE_Body, TOE_Title, TOE_Color, TOE_Author, TOE_Image):
        if part == 'title':
            edited = discord.Embed(title=text, description=TOE_Body, color=TOE_Color)
            if TOE_Image == edited.Empty:
                pass
            else:
                edited.set_image(url=TOE_Image)
        if part == 'body':
            edited = discord.Embed(title=TOE_Title, description=f'{TOE_Body}\n`EDIT:`\n{text}', color=TOE_Color)
            if TOE_Image == edited.Empty:
                pass
            else:
                edited.set_image(url=TOE_Image)
        if part == 'image':
            edited = discord.Embed(title=TOE_Title, description=TOE_Body, color=TOE_Color)
            if text == 'Blank':
                pass
            else:
                edited.set_image(url=text)
        edited.set_author(name=TOE_Author.name, icon_url=TOE_Author.icon_url)
        return edited

    async def thread_edit_announcment(author, part):
        if part == 'title':
            embed=discord.Embed(title="Thread OP edited!", description=f"{author} has changed the title of this thread.", color=THREAD_STATE_CHANGE)
        if part == 'body':
            embed=discord.Embed(title="Thread OP edited!", description=f"{author} has added text to the body of the thread.", color=THREAD_STATE_CHANGE)        
        if part == 'image':
            embed=discord.Embed(title="Thread OP edited!", description=f"{author} has changed the image in the OP", color=THREAD_STATE_CHANGE)
        embed.set_author(name=author.guild.name, icon_url=author.guild.icon_url)
        embed.set_footer(text=f"Thread edited on: {datetime.now().strftime('%B %d at %H:%M')}")
        return embed

    async def thread_edit_mod(part, text, mod, TOE_Body, TOE_Title, TOE_Color, TOE_Author, TOE_Image):
        if part.lower() == 'title':
            edited = discord.Embed(title=text, description=TOE_Body, color=TOE_Color)
            if TOE_Image == edited.Empty:
                pass
            else:
                edited.set_image(url=TOE_Image)
        if part.lower() == 'body':
            edited = discord.Embed(title=TOE_Title, description=f'{TOE_Body}\n`MOD EDIT:`\n{text}', color=TOE_Color)
            if TOE_Image == edited.Empty:
                pass
            else:
                edited.set_image(url=TOE_Image)
        if part == 'image':
            edited = discord.Embed(title=TOE_Title, description=TOE_Body, color=TOE_Color)
            if text == 'Blank':
                pass
            else:
                edited.set_image(url=text)
        edited.set_author(name=TOE_Author.name, icon_url=TOE_Author.icon_url)
        edited.set_footer(text=f"Moderator {mod} edited this message on: {datetime.now().strftime('%B %d at %H:%M')}")
        return edited

    async def thread_edit_mod_announcment(mod, part):
        if part == 'title':
            embed=discord.Embed(title="Thread OP edited!", description=f"{mod} has changed the title of this thread.", color=THREAD_STATE_CHANGE)
        if part == 'body':
            embed=discord.Embed(title="Thread OP edited!", description=f"{mod} has added text to the body of the thread.", color=THREAD_STATE_CHANGE)
        if part == 'image':
            embed=discord.Embed(title="Thread OP edited!", description=f"{mod} has changed the image in the OP", color=THREAD_STATE_CHANGE)
        embed.set_author(name=mod.guild.name, icon_url=mod.guild.icon_url)
        embed.set_footer(text=f"Thread edited on: {datetime.now().strftime('%B %d at %H:%M')}")
        return embed

    async def thread_locked(mod, reason):
        nl = '\n'
        embed=discord.Embed(title=":lock: THREAD LOCKED :lock:", description=f"This thread has been **__locked__**!{nl}Responsible Moderator: **{mod}**{nl}Reason for lock: **{reason}**", color=THREAD_STATE_CHANGE)
        embed.set_author(name=mod.guild.name, icon_url=mod.guild.icon_url)
        embed.set_footer(text=f"Thread locked on: {datetime.now().strftime('%B %d at %H:%M')}")
        return embed

    async def thread_unlocked(mod):
        embed=discord.Embed(title=":unlock: THREAD UNLOCKED :unlock:", description=f"This thread is now **__unlocked__**!\nResponsible Moderator: **{mod}**", color=THREAD_STATE_CHANGE)
        embed.set_author(name=mod.guild.name, icon_url=mod.guild.icon_url)
        embed.set_footer(text=f"Thread unlocked locked on: {datetime.now().strftime('%B %d at %H:%M')}")
        return embed

    async def inactive_lock(thread):
        embed=discord.Embed(title=":lock: THREAD LOCKED :lock:", description=f"This thread has been **__locked__**!\nThe last message in this thread was over 3 days ago. In 24 hours, this channel will be deleted. Take this time to save any valuable information.", color=THREAD_STATE_CHANGE)
        embed.set_author(name=thread.guild.name, icon_url=thread.guild.icon_url)
        embed.set_footer(text=f"Thread locked on: {datetime.now().strftime('%B %d at %H:%M')}")
        return embed

    async def make_thread(ctx, step):
        if step == 1:
            embed=discord.Embed(title="What do you want the title of the thread to be? (The title is this part)", description='Type your title out. Keep it brief please!', color=DEFAULT_COLOR)
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
            embed.set_footer(text='Type abort to stop thread creation.')
        elif step == 2:
            embed=discord.Embed(title="OK, we got your title done. Now what do you want to talk about?", description='Your thoughts and questions will be here.', color=DEFAULT_COLOR)
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
            embed.set_footer(text='Type abort to stop thread creation.')
        return embed

    async def manual_creation(ctx, thread):
        embed=discord.Embed(title=thread.get(1), description=thread.get(2), color=DEFAULT_COLOR)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        return embed

    async def keep_thread(ctx, setting):
        if setting:
            embed = discord.Embed(title='Thread preservation setting: Keep', description=f'This thread __***will not be deleted***__  if it goes inactive. To reverse this, simply run `{ctx.prefix}{ctx.invoked_with}` again.', color=THREAD_STATE_CHANGE)
        else:
            embed = discord.Embed(title='Thread preservation setting: Do Not Keep', description=f'This thread __***will be deleted***__ if it goes inactive. To reverse this, simply run `{ctx.prefix}{ctx.invoked_with}` again.', color=THREAD_STATE_CHANGE)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        return embed

    async def thelp(ctx):
        embed=discord.Embed(title="Help Menu", description="Command descriptions and syntax's", color=DEFAULT_COLOR)
        embed.set_author(name=ctx.bot.user, icon_url=ctx.bot.user.avatar_url)
        support_guild = ctx.bot.get_guild(475094347583586324)
        embed.set_thumbnail(url=support_guild.icon_url)
        embed.add_field(name=f':small_orange_diamond: ***{ctx.prefix}tmake***', value='Takes you through the steps of creating a thread.\nTakes no arguments.', inline=False)
        embed.add_field(name=f':small_orange_diamond: ***{ctx.prefix}tedit***', value=f'Let\'s you edit the thread\'s OP.\nFirst argument can be either `title`, `body` or `image`.\nSecond argument is the text you wish to change/append.\nIf the second argument is `image`, you can upload an image with your command or just provide a url to an image\nInvoker must either be the owner of the thread or have the `manage_message` permission.\n\nExample: `{ctx.prefix}tedit title The Super Shotty is actual trash.`', inline=False)
        embed.add_field(name=f':small_orange_diamond: ***{ctx.prefix}tdelete***', value='Delete\'s the thread.\nTakes no arguments.\nCan only be used in thread channels.\nInvoker must either own the thread or have the `manage_channels` permission', inline=False)
        embed.add_field(name=f':small_orange_diamond: ***{ctx.prefix}tlock***', value=f'Locks a thread.\nOne optional argument.\nCan only be used in thread channels.\nWill set the `send_message` permission to `False` to all roles that can view the channel. If a role has the `manage_message permission`, they will still be able to post.\n\nExample: `{ctx.prefix}tlock Super Shotty is fine. Git Gud.`', inline=False)
        embed.add_field(name=f':small_orange_diamond: ***{ctx.prefix}tunlock***', value='Unlocks a thread. Will restore permissions back to their original values when .tlock was ran.\nTakes no arguments.', inline=False)
        embed.add_field(name=f':small_orange_diamond: ***{ctx.prefix}tcreate***', value=f'Allows you to create categories for threads.\nIn order to use this command, you need the `manage_channels` permission.\nThis will create a channel in the category that will stay at the top of the category. Members need to use this channel to put their thread in the category. the messages the `{ctx.prefix}tmake` post will be deleted to keep the channel clean.\n\nExample: `{ctx.prefix}tcreate Relational Databases`', inline=False)
        embed.add_field(name=f':small_orange_diamond: ***{ctx.prefix}tdc***', value='Deletes a category and *all* channels in that category. You must have the `manage_guild` permission to run this. You will need to do a verification step before this command gets executed.', inline=False)
        embed.add_field(name=f':small_orange_diamond: ***{ctx.prefix}tprefix***', value=f'Lets you set the guilds custom prefix.\nOnly people with the `manage_channels` permission can run this.\nPrefix cannot exceed 5 characters.\n\nExample: `{ctx.prefix}tprefix !`')
        embed.add_field(name=f':small_orange_diamond: ***{ctx.prefix}im***', value='Get a link so you can invite me to your server.')
        embed.set_footer(text="Join this bots help server at: https://discord.gg/M8DmU86 for assistance and updates.")
        return embed

    async def hub_channel(ctx, category):
        embed=discord.Embed(title="THREAD HUB CHANNEL", description=f'Please create threads for the category `{category[:96]}` here.', color=DEFAULT_COLOR)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        return embed

    async def category_made(ctx, custom_category_hub_channel):
        embed=discord.Embed(title="Category created!", description=f'Please use {custom_category_hub_channel.mention} to place threads into this category. I\'ve left a reminder in there too.', color=DEFAULT_COLOR)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text='You can rename this channel to whatever you wish. You can also move the category around.')
        return embed

def setup(bot):
    bot.add_cog(TB_Embeds(bot))
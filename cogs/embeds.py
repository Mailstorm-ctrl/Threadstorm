import discord
from datetime import datetime
from discord.ext import commands

Default_color = 0x69dce3
Thread_locked = None

class TB_Embeds(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def potential_threads(choices, me):
        embed=discord.Embed(title="Potential Thread Topics", description="I've scanned the last few messages and these are some of the potential topics I found.", color=Default_color)
        embed.set_author(name=me.user.name, icon_url=me.user.avatar_url)
        counter = 0
        for topic in choices.keys():
            embed.add_field(name=f'{topic}', value=choices.get(topic)[1], inline=True)
            counter += 1
        embed.add_field(name=f'{counter}: Custom', value="Selecting this option will ask you what message you want to create a topic on. Select the message by reaction with whatever you feel like.")
        embed.set_footer(text="If you want to skip this step, you can provide the ID of the message you want to create a topic on during the initial command.")
        return embed

    async def thread_created(thread_id):
        embed=discord.Embed(title="Success!", description=f"Your requested thread was made! Thread ID: {thread_id}", color=Default_color)
        return embed

    async def thread_op_author(channel, author, thread_id):
        """Called when a user makes a thread. Notified the message author"""
        nl = '\n'
        embed=discord.Embed(title="A thread was made with your message!", description=f"{author.name} has created a thread in {author.guild.name} using your message!", color=Default_color)
        embed.set_author(name=author.guild.name, icon_url=author.guild.icon_url)
        embed.add_field(name='Thread Information:', value=f"Your thread can be found at {channel.mention}.{nl}{nl}If you want to edit the OP, you can run `!tedit <title | body> <Text to update/add>` in the channel")
        embed.set_footer(text=f"If you do not want this to be a thread. Get a moderator to delete it. The ID of the thread created is: {thread_id}")
        return embed

    async def thread_op(msg):
        """The Threads Original Post"""
        embed=discord.Embed(title=msg.content[:17]+'...', description=f"{msg.content}", color=Default_color)
        embed.set_author(name=msg.author.name, icon_url=msg.author.avatar_url)
        return embed

    async def thread_edit_nm(part, text, TOE_Body, TOE_Title, TOE_Color, TOE_Author):
        if part.lower() == 'title':
            edited = discord.Embed(title=text, description=TOE_Body, color=TOE_Color)
        if part.lower() == 'body':
            nl = '\n'
            edited = discord.Embed(title=TOE_Title, description=f'{TOE_Body}{nl}`EDIT:`{nl}{text}', color=TOE_Color)
        edited.set_author(name=TOE_Author.name, icon_url=TOE_Author.icon_url)
        return edited

    async def thread_edit_announcment(author, part):
        if part == 'title':
            embed=discord.Embed(title="Thread OP edited!", description=f"{author} has changed the title of this thread.", color=Default_color)
        if part == 'body':
            embed=discord.Embed(title="Thread OP edited!", description=f"{author} has added text to the body of the thread.", color=Default_color)        
        embed.set_author(name=author.guild.name, icon_url=author.guild.icon_url)
        embed.set_footer(text=f"Thread edited on: {datetime.now().strftime('%B %d at %H:%M')}")
        return embed

    async def thread_edit_mod(part, text, mod, TOE_Body, TOE_Title, TOE_Color, TOE_Author):
        if part.lower() == 'title':
            edited = discord.Embed(title=text, description=TOE_Body, color=TOE_Color)
        if part.lower() == 'body':
            nl = '\n'
            edited = discord.Embed(title=TOE_Title, description=f'{TOE_Body}{nl}`MOD EDIT:`{nl}{text}', color=TOE_Color)
        edited.set_author(name=TOE_Author.name, icon_url=TOE_Author.icon_url)
        edited.set_footer(text=f"Moderator {mod} edited this message on: {datetime.now().strftime('%B %d at %H:%M')}")
        return edited

    async def thread_edit_mod_announcment(mod, part):
        if part == 'title':
            embed=discord.Embed(title="Thread OP edited!", description=f"{mod} has changed the title of this thread.", color=Default_color)
        if part == 'body':
            embed=discord.Embed(title="Thread OP edited!", description=f"{mod} has added text to the body of the thread.", color=Default_color)
        embed.set_author(name=mod.guild.name, icon_url=mod.guild.icon_url)
        embed.set_footer(text=f"Thread edited on: {datetime.now().strftime('%B %d at %H:%M')}")
        return embed

    async def thread_locked(mod, reason):
        nl = '\n'
        embed=discord.Embed(title=":lock: THREAD LOCKED :lock:", description=f"This thread has been **__locked__**!{nl}Responsible Moderator: **{mod}**{nl}Reason for lock: **{reason}**", color=Default_color)
        embed.set_author(name=mod.guild.name, icon_url=mod.guild.icon_url)
        embed.set_footer(text=f"Thread locked on: {datetime.now().strftime('%B %d at %H:%M')}")
        return embed

    async def inactive_lock(guild):
        nl = '\n'
        embed=discord.Embed(title=":lock: THREAD LOCKED :lock:", description=f"This thread has been **__locked__**!{nl}The last message in this thread was over 3 days ago. In 24 hours, this channel will be deleted. Take this time to save any valuable information.", color=Default_color)
        embed.set_author(name=guild.name, icon_url=guild.icon_url)
        embed.set_footer(text=f"Thread locked on: {datetime.now().strftime('%B %d at %H:%M')}")
        return embed

def setup(bot):
    bot.add_cog(TB_Embeds(bot))
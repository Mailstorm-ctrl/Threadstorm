import discord
import typing
import json
from datetime import datetime,timezone
from discord.ext import tasks, commands

class TB_Editing(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    async def embed_check(self, embed):
        bad_fields = []
        if len(embed) > 6000:
            bad_fields.append("Length of embed to long. Total length cannot exceed 6000 characters.")
        if len(embed.title) > 256:
            bad_fields.append("Title is over 256 characters long.")
        if len(embed.description) > 2048:
            bad_fields.append("Description is over 2048 characters long.")
        if len(embed.fields) > 25:
            bad_fields.append("Field count is over 25.")
        for field in embed.fields:
            if len(field.name) > 256:
                bad_fields.append(f"Field name {field.name} exceeds 256 characters.")
            if len(field.value) > 1024:
                bad_fields.append(f"Field value under {field.name} exceeds 1024 characters.")
 
        if bad_fields:
            embed = discord.Embed(title="Errors in embed", description="It seems like your thread will be to long, or a general failure has occured.\nCorrect these errors then try again.", color=self.bot.warning_color)
            embed.add_field(name="Errors:", value='\n'.join(bad_fields), inline=False)
            return [embed, False]

        return [embed, True]

    async def parse_json(self, json_file_bytes, ctx, mod_edit):
        """Read the json file into a dict. Check for errors and length restrictions. return errors or return the formatted embed"""
        error = []
        try:
            json_obj = json.loads(json_file_bytes.decode('utf8'))
        except Exception as e:
            error.append('Unable to convert JSON file. Please make sure it\'s formatted correctly.')
            error.append(str(e))
            embed = discord.Embed(title="Bad format", description="See below for a detailed error.", color=self.bot.warning_color)
            embed.add_field(name="Errors:", value='\n'.join(error), inline=False)
            return [embed, False]

        try:
            embeds = []
            for embed in json_obj['embeds']:
                embeds.append(discord.Embed.from_dict(embed))
        except Exception as e:
            embed = discord.Embed(title="Bad format", description="See below for a detailed error.", color=self.bot.warning_color)
            embed.add_field(name="Error:", value=f"Unable to read JSON. Make sure it's in the format Discord expects. You can use [this](https://discohook.org) website for creating embeds. Just beaware the content field wont be posted!\nError: {e}", inline=False)
            return [embed, False]

        bad_fields = []
        for embed in embeds:
            if len(embed) > 6000:
                bad_fields.append("Length of embed to long. Total length cannot exceed 6000 characters.")
            if len(embed.title) > 256:
                bad_fields.append("Title is over 256 characters long.")
            if len(embed.description) > 2048:
                bad_fields.append("Description is over 2048 characters long.")
            if len(embed.fields) > 25:
                bad_fields.append("Field count is over 25.")
            for field in embed.fields:
                if len(field.name) > 256:
                    bad_fields.append(f"Field name {field.name} exceeds 256 characters.")
                if len(field.value) > 1024:
                    bad_fields.append(f"Field value under {field.name} exceeds 1024 characters.")
 
        if bad_fields:
            embed = discord.Embed(title="Errors in JSON", description="It seems like your JSON file is to long in some spots, or a general failure has occured.\nCorrect these errors then try again.", color=self.bot.warning_color)
            embed.add_field(name="Errors:", value='\n'.join(bad_fields), inline=False)
            return [embed, False]

        return [embed, True]

    @commands.command(name='editthread',aliases=['tedit'], description='Editing an existing thread.')
    @commands.guild_only()
    async def edit(self, ctx, part=None, *, appended_text: typing.Optional[str] = 'Blank'):
        """This lets server mods and thread owners to edit their own thread. This only APPENDS text (Except the title). It does not modify!"""
        
        # Check to see if this is even in the cache
        if ctx.channel.id not in self.bot.cache[ctx.guild.id]['active_threads']:
            embed = discord.Embed(title="Channel not in-cache or not ran in thread channel", colour=self.bot.warning_color, description="Please run this in the channel you wish to edit. If you are, there seems to be an error and this thread is no longer being recognized.")
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_author(name="Threadstorm", url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return
        
        valid_args = ['title','description','body','picture','json']
        # See if user supplied valid arguments.
        # Display an error if they didn't
        if part is None or part not in valid_args:
            embed = discord.Embed(title="Missing arguments", colour=self.bot.warning_color, description=f"It seems you are missing some arguments. Valid arguments are: `{', '.join(valid_args)}`")
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_author(name="Threadstorm", url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return
        
        # See to see the thread was made with a json file and the user didn't supply a json file
        if self.bot.cache[ctx.guild.id]['active_threads'][ctx.channel.id]['json'] and not ctx.message.attachments:
            embed = discord.Embed(title="JSON-based Thread", colour=self.bot.warning_color, description="A JSON file was used to create this thread. Therefore, another json file is needed in order to edit this thread. Please supply a valid json file.")
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_author(name="Threadstorm", url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=self.bot.user.avatar_url)
            embed.set_footer(text="Reminder! One embed per thread. If you supply a file with multiple embeds, only the last one will be kept.")
            await ctx.send(embed=embed)
            return

        # Check for permission to edit thread
        mod_edit = False
        if ctx.author.id != self.bot.cache[ctx.guild.id]['active_threads'][ctx.channel.id]['author_id'] and ctx.author.guild_permissions.manage_channels:
            mod_edit = True
        if ctx.author.id != self.bot.cache[ctx.guild.id]['active_threads'][ctx.channel.id]['author_id'] and not ctx.author.guild_permissions.manage_channels:
            embed = discord.Embed(title="403 -- FORBIDDEN", colour=self.bot.warning_color, description="You do not have the proper permission to edit this thread. You either need to have the manage_message guild permission or be the owner of the thread.")
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_author(name="Threadstorm", url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return

        thread_op_msg = await ctx.channel.fetch_message(self.bot.cache[ctx.guild.id]['active_threads'][ctx.channel.id]['original_msg_id'])

        # Check to see if user supplied a json file and provided the right argument
        if self.bot.cache[ctx.guild.id]['active_threads'][ctx.channel.id]['json'] and ctx.message.attachments and part.lower() == 'json':
            json_bytes = await ctx.message.attachments[0].read(use_cached=False)
            new_embed = await self.parse_json(json_bytes, ctx, mod_edit)
            if new_embed[1] == False:
                await ctx.send(embed=new_embed[0])
                return
            
            new_embed[0].set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            if len(thread_op_msg.embeds[0].footer.text) == 13:
                if mod_edit:
                    new_embed[0].set_footer(text=f"{thread_op_msg.embeds[0].footer.text} MOD > {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")
                else:
                    new_embed[0].set_footer(text=f"{thread_op_msg.embeds[0].footer.text} {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")
            else:
                if mod_edit:
                    new_embed[0].set_footer(text=f"{thread_op_msg.embeds[0].footer.text} | MOD > {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")
                else:
                    new_embed[0].set_footer(text=f"{thread_op_msg.embeds[0].footer.text} | {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")

            await thread_op_msg.edit(embed=new_embed[0])
            embed = discord.Embed(title="Thread Updated", colour=self.bot.success_color, description="The original thread has been replaced with the file specified.")
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_author(name="Threadstorm", url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return

        thread_embed = thread_op_msg.embeds[0]

        # Section to edit the thread title
        # If the invoking user doesn't own the thread, append the MOD edit tag
        if part.lower() == 'title':
            thread_embed.title = appended_text
            if len(thread_embed.footer.text) == 13:
                if mod_edit:
                    thread_embed.set_footer(text=f"{thread_embed.footer.text} MOD > {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")
                else:
                    thread_embed.set_footer(text=f"{thread_embed.footer.text} {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")
            else:
                if mod_edit:
                    thread_embed.set_footer(text=f"{thread_embed.footer.text} | MOD > {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")
                else:
                    thread_embed.set_footer(text=f"{thread_embed.footer.text} | {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")
            result = await self.embed_check(thread_embed)
            if result[1]:
                await thread_op_msg.edit(embed=thread_embed)
                await ctx.channel.edit(name=appended_text)
                embed = discord.Embed(title="Thread Updated", colour=self.bot.success_color, description="The thread title has been replaced.")
                embed.set_thumbnail(url=ctx.guild.icon_url)
                embed.set_author(name="Threadstorm", url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)
                return
            else:
                errors = '\n'.join(result[1])
                await ctx.send(f"Bad embed. Errors: {errors}")
                return

        # Section to edit the thread body
        # If the invoking user doesn't own the thread, append the MOD edit tag
        if part.lower() in ['description', 'body']:
            thread_embed.description += f"\nEDIT: {appended_text}"
            if len(thread_embed.footer.text) == 13:
                if mod_edit:
                    thread_embed.set_footer(text=f"{thread_embed.footer.text} MOD > {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")
                else:
                    thread_embed.set_footer(text=f"{thread_embed.footer.text} {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")
            else:
                if mod_edit:
                    thread_embed.set_footer(text=f"{thread_embed.footer.text} | MOD > {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")
                else:
                    thread_embed.set_footer(text=f"{thread_embed.footer.text} | {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")
            result = await self.embed_check(thread_embed)
            if result[1]:
                await thread_op_msg.edit(embed=thread_embed)
                embed = discord.Embed(title="Thread Updated", colour=self.bot.success_color, description="Your requested addition as been appended.")
                embed.set_thumbnail(url=ctx.guild.icon_url)
                embed.set_author(name="Threadstorm", url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)
                return
            else:
                errors = '\n'.join(result[1])
                await ctx.send(f"Bad embed. Errors: {errors}")
                return

        # Section to edit the threads picture
        # If the invoking user doesn't own the thread, append the MOD edit tag
        if part.lower() == 'picture':
            if ctx.message.attachments:
                thread_embed.set_image(url=ctx.message.attachments[0].url)
                if len(thread_embed.footer.text) == 13:
                    if mod_edit:
                        thread_embed.set_footer(text=f"{thread_embed.footer.text} MOD > {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")
                    else:
                        thread_embed.set_footer(text=f"{thread_embed.footer.text} {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")
                else:
                    if mod_edit:
                        thread_embed.set_footer(text=f"{thread_embed.footer.text} | MOD > {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")
                    else:
                        thread_embed.set_footer(text=f"{thread_embed.footer.text} | {datetime.utcnow().strftime('%m/%d, %H:%M %p')}")
                await thread_op_msg.edit(embed=thread_embed)
                embed = discord.Embed(title="Thread Updated", colour=self.bot.success_color, description="Thread picture updated.")
                embed.set_thumbnail(url=ctx.guild.icon_url)
                embed.set_author(name="Threadstorm", url="https://github.com/Mailstorm-ctrl/Threadstorm", icon_url=self.bot.user.avatar_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Please upload the picture you're trying to display with your command.")
                return
        
        if part.lower() == 'json':
            await ctx.send("This thread wasn't made with a json file. Therefore, you cannot use this argument. Sorry!")
            return


    @commands.command(name='keep', aliases=['tkeep'], description='Toggle the delete flag')
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def keep(self, ctx, thread: typing.Optional[discord.TextChannel] = None):
        """Pretty simple. Toggles the value that determines if a thread should be created or not"""
        thread_link = None
        if thread is not None and thread.id in self.bot.cache[ctx.guild.id]['active_threads']:
            self.bot.cache[ctx.guild.id]['active_threads'][thread.id]['keep'] = not self.bot.cache[ctx.guild.id]['active_threads'][thread.id]['keep']
            thread_link = thread.id
        else:
            if ctx.channel.id in self.bot.cache[ctx.guild.id]['active_threads']:
                self.bot.cache[ctx.guild.id]['active_threads'][ctx.channel.id]['keep'] = not self.bot.cache[ctx.guild.id]['active_threads'][ctx.channel.id]['keep']
                thread_link = ctx.channel.id
            else:
                await ctx.send("Unable to modified channel. Channel ID not found. A database error has occured or this channel is not managed by me.")
                return
        thread_id = thread_link
        thread_link = f"https://discord.com/channels/{ctx.guild.id}/{thread_link}"
        embed=discord.Embed(title="Thread settings updated", description=f"You have changed the **keep** flag for [this]({thread_link}) thread.\nThe current value is: `{self.bot.cache[ctx.guild.id]['active_threads'][thread_id]['keep']}`", color=self.bot.success_color)
        embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text="A True value means the thread will not be marked for deletion due to inactivity. A False value means a thread will get marked for deletion if it's inactive to long.")            
        await ctx.send(embed=embed)
        await self.bot.write_db(ctx.guild)


def setup(bot):
    bot.add_cog(TB_Editing(bot))

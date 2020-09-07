import discord
import asyncio
import typing
import json
from datetime import datetime
from discord.ext import commands

## Will probably just make my own system for cooldowns
# class CustomCooldown:
#     def __init__(self, rate: int, per: float, alter_rate: int, alter_per: float, bucket: commands.BucketType, ctx, *, elements):
#         self.elements = elements
#         self.default_mapping = commands.CooldownMapping.from_cooldown(rate, per, bucket)
#         self.altered_mapping = commands.CooldownMapping.from_cooldown(alter_rate, alter_per, bucket)
#         rate = ctx.bot.cache[ctx.guild.id]["settings"]["cooldown"]["rate"]
#         per = ctx.bot.cache[ctx.guild.id]["settings"]["cooldown"]["per"]
#         bucket_str = ctx.bot.cache[ctx.guild.id]["settings"]["cooldown"]["bucket"]
#         if bucket_str == "user":
#             pass
#         if bucket_str == "guild":
#             pass
#         if bucket_str == "channel":
#             pass
#         if bucket_str == "member":
#             pass
#         if bucket_str == "category":
#             pass
#         if bucket_str == "role":
#             pass


#     def __call__(self, ctx: commands.Context):
#         key = self.altered_mapping._bucket_key(ctx.message)
#         if key in self.elements:
#             bucket = self.altered_mapping.get_bucket(ctx.message)
#         else:
#             bucket = self.default_mapping.get_bucket(ctx.message)
#         retry_after = bucket.update_rate_limit()
#         if retry_after:
#             raise commands.CommandOnCooldown(bucket, retry_after)
#         return True

class TB_Thread_Creation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def has_required_role(ctx):
        """Check to see if guild has role requirements, then see if author meets requirements"""
        if ctx.bot.cache[ctx.guild.id]['settings']["role_required"]:
            return any(item in [role.id for role in ctx.author.roles] for item in ctx.bot.cache[ctx.guild.id]['settings']["allowed_roles"])
        else:
            return True


    async def parse_json(self, json_file_bytes, ctx):
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
            # Need to change some properties to keep consistency
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_footer(text="Edit History:")
 
        if bad_fields:
            embed = discord.Embed(title="Errors in JSON", description="It seems like your JSON file is to long in some spots, or a general failure has occured.\nCorrect these errors then try again.", color=self.bot.warning_color)
            embed.add_field(name="Errors:", value='\n'.join(bad_fields), inline=False)
            return [embed, False]

        return [embed, True]



    async def create_thread(self, data):
        embed = discord.Embed(title=data['title'], description=data['description'], color=self.bot.DEFAULT_COLOR)
        embed.set_author(name=data['author'].name, icon_url=data['author'].avatar_url)
        embed.set_footer(text="Edit History:")
        return embed



    def manual_creation(self, ctx, step):
        if step == 1:
            embed=discord.Embed(title="What do you want the title of the thread to be? (The title is this part)", description='Type your title out. Keep it brief please!', color=self.bot.DEFAULT_COLOR)
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
            embed.set_footer(text='Type abort to stop thread creation.')
        elif step == 2:
            embed=discord.Embed(title="OK, we got your title done. Now what do you want to talk about?", description='Your thoughts and questions will be here.', color=self.bot.DEFAULT_COLOR)
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
            embed.set_footer(text='Type abort to stop thread creation.')
        return embed

    def fill_cache(self, thread_channel, ctx, thread_op, category, json):
        self.bot.cache[ctx.guild.id]['active_threads'][thread_channel.id] = {}
        self.bot.cache[ctx.guild.id]['active_threads'][thread_channel.id]['last_message_time'] = datetime.now()
        self.bot.cache[ctx.guild.id]['active_threads'][thread_channel.id]['keep'] = False
        self.bot.cache[ctx.guild.id]['active_threads'][thread_channel.id]['author_id'] = ctx.author.id
        self.bot.cache[ctx.guild.id]['active_threads'][thread_channel.id]['original_msg_id'] = thread_op.id
        self.bot.cache[ctx.guild.id]['active_threads'][thread_channel.id]['json'] = json
        self.bot.cache[ctx.guild.id]['active_threads'][thread_channel.id]['category'] = category.id

    @commands.command(name='makethread',aliases=['tmake'], description='Make a new thread')
    @commands.cooldown(2, 7200,type=commands.BucketType.member)
    @commands.bot_has_permissions(manage_messages=True, manage_channels=True)
    @commands.guild_only()
    @commands.check(has_required_role)
    # Need to use tuple for consume rest instead. Easier, efficient
    async def manual_create(self, ctx, *thread):
        """Create a thread. You can ether run the command by itself and follow the prompts, invoke the command with a properly formatted JSON attached, or use the `-t`(title) and `-b`(body) flags to create a thread with one message. """        
        if ctx.guild.id not in self.bot.cache:
            await ctx.send(f"I don't remember this guild. Perhaps I joined without the proper permissions? Find someone that has the `manage_guild` permission and tell them to run `{ctx.prefix}tsetup`")
        
        # Try and find the channel used for posting threads in
        # If it isn't found, abort the creation
        # In a try block incase a server isn't using categories for whatever reason
        try:
            if ctx.channel.category.id in [channel_id for channel_id in self.bot.cache[ctx.guild.id]["custom_categories"].keys()]:
                category = ctx.channel.category
            else:
                category = ctx.guild.get_channel(self.bot.cache[ctx.guild.id]["default_thread_channel"])
                if category is None:
                    category = await ctx.guild.fetch_channel(self.bot.cache[ctx.guild.id]["default_thread_channel"])
                    if category is None:
                        await ctx.send(f"No thread category found. Please run {ctx.prefix}tsetup.\n\nBe warned, running this command will essentially wipe the data for this server. Any active threads and custom categories will be forgotten.")
                        return
        except:
            pass

        thread_data = {}
        thread_data['author'] = ctx.author
        messages = [ctx.message]

        # See if user supplied a file, mainly a json used to make their thread.
        # Highly customizable
        if ctx.message.attachments:
            json_bytes = await ctx.message.attachments[0].read(use_cached=False)
            thread_op_msg = await self.parse_json(json_bytes, ctx)
            if thread_op_msg[1] == False:
                await ctx.send(embed=thread_op_msg[0])
                return
            thread_channel = await category.create_text_channel(thread_op_msg[0].title, overwrites=ctx.channel.overwrites)
            thread_op = await thread_channel.send(embed=thread_op_msg[0])
            await thread_op.pin()
            embed = discord.Embed(title="Success!", description=f"Your requested thread was made! It can be found at {thread_channel.mention}", color=self.bot.success_color)
            embed.set_footer(text='This thread has the same permissions as this channel does.')
            await ctx.send(embed=embed)
            self.fill_cache(thread_channel, ctx, thread_op, category, True)
            await self.bot.write_db(ctx.guild)
            return

        else:            
            cli = False
            if len(thread) > 0:
                title = []
                body = []
                track = 0
                found = []
                for i,item in enumerate(thread):
                    if item == "-t":
                        track += 1
                        found.append("-t")
                        # Title flag found. Start at that index and append text until "-b" is hit or out of options
                        for opt in thread[i+1:]:
                            if opt == "-b":
                                break
                            title.append(opt)
                    if item == "-b":
                        track += 1
                        found.append("-b")
                        # body flag found. Start at that index and append text until "-t" is hit or out of options
                        for opt in thread[i+1:]:
                            if opt == "-t":
                                break
                            body.append(opt)
                if track < 2:
                    missing = ["-t", "-b"]
                    try:
                        missing.remove(found[0])
                    except:
                        pass
                    await ctx.send(f"Missing flag(s): `{', '.join(missing)}`\nPlease rerun with all required flags set.")
                    return
                cli = True
                thread_data['title'] = ' '.join(title)
                thread_data['description'] = ' '.join(body) 

            # Go through and create a thread from scratch.
            if not cli:
                content = []
                abort = 'no'
                for i in range(2):
                    if abort == 'abort' or i > 2:
                        break
                    text = await ctx.send(embed=self.manual_creation(ctx,i+1))
                    messages.append(text)
                    try:
                        msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=180)
                    except asyncio.TimeoutError:
                        await ctx.send("Timeout reached. These messages timeout after 3 minutes. Try typing what you want to say before initiating this command.")
                        return
                    else:
                        messages.append(msg)
                        abort = msg.content
                        if i == 0:
                            thread_data['title'] = msg.content
                        else:
                            thread_data['description'] = msg.content
                if abort == 'abort':
                    await ctx.send("Thread creation aborted. User provoked.")
                    for msg in messages:
                        await msg.delete()
                    return
            
            # Final stage. Create the embed for the thread, post it, pin it, add to cache, add to database [TODO]
            embed = await self.create_thread(thread_data)
            thread_channel = await category.create_text_channel(thread_data['title'], topic=thread_data['description'], overwrites=ctx.channel.overwrites)
            thread_op = await thread_channel.send(embed=embed)
            await thread_op.pin()

            if self.bot.cache[ctx.guild.id]['settings']['cleanup']:
                for msg in messages:
                    await msg.delete()

            embed = discord.Embed(title="Success!", description=f"Your requested thread was made! It can be found at {thread_channel.mention}", color=self.bot.success_color)
            embed.set_footer(text='This thread has the same permissions as this channel does.')
            await ctx.send(embed=embed)
            self.fill_cache(thread_channel, ctx, thread_op, category, False)
            await self.bot.write_db(ctx.guild)



def setup(bot):
    bot.add_cog(TB_Thread_Creation(bot))

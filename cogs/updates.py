import discord
import asyncio
from discord.ext import tasks, commands

class TB_updates(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot_update_status.start()

    @commands.command(name="update", aliases=['pn', 'patchnotes', 'tupdate'], description="Show the most recent patchnotes")
    async def pn(self, ctx):
        embed = discord.Embed(title="One Year Later... (Thank You & Patch Notes)", colour=discord.Colour(0xffff), url="https://github.com/Mailstorm-ctrl/Threadstorm", description="It's been about a year since I launched this bot. It's grown far more than I ever imagined it would. I thought maybe it would top out at 60 or 70 servers but it's doubled that and keeps going up. So for that, I thank you all for showing me this bot is useful to your communities.\n\nWith that, I've released a pretty big update. It adds a lot of features a bot of this nature should of had to begin with. So here they are.")
        AppInfo = await self.bot.application_info()
        embed.set_author(name="Mailstorm", icon_url=AppInfo.owner.avatar_url)
        embed.set_thumbnail(url=AppInfo.icon_url)
        embed.set_footer(text=f"To learn how to use these new features use the {ctx.prefix}thelp command, read the readme on github, or join the support server")
        embed.add_field(name="Patch Notes", value=f"```patch\n+ {ctx.prefix}tmake can accept JSON files to make more customized threads\n\n+ Threads can be made in one message with the {ctx.prefix}tmake command\n\n+ Guilds can now restrict {ctx.prefix}tmake to certain roles only and toggle the restriction\n\n+ Additionally, some roles can be allowed to bypass the cooldown\n\n+ Guilds can choose how long to wait until a thread is marked as \"inactive\"\n\n+ Automatic cleanup of commands and messages used to make a thread. This can be toggled\n\n+ A way to view all of your guilds settings (excluding active threads and categories) in one command\n\n+ Database improvements\n\n+ Optimizations. More cache, less database\n\n+ Deleted categories will attempt to recreate themselves (View_Audit_Log permission needed)\n\n- Cooldowns are still in place until I figure out how to make custom per-guild cooldowns work.```", inline=False)
        embed.add_field(name="Potential Issues", value="I essentially rewrote this bot to be more efficient and easier to add and fix features. With this, the old format needed to be converted to the new format. If you find there are any issues with existing threads, please [join the support server](https://discord.com/invite/M8DmU86) and give me some details on what's happening!", inline=False)
        await ctx.send(embed=embed)

    @tasks.loop(minutes=15)
    async def bot_update_status(self):
        await asyncio.sleep(60)
        activity = discord.Activity(type=discord.ActivityType.watching,
                                    name=f"Update released! .tupdate")
        await self.bot.change_presence(activity=activity)

    @bot_update_status.before_loop
    async def wait3(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(TB_updates(bot))
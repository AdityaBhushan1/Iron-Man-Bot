import discord,os
from discord.ext import commands
import asyncio
import random
import sys
import traceback
import jishaku
import asyncpg
from cogs.utils import context
from cogs.utils.help import HelpCommand
from cogs.utils.buttons import SelfRoles
from colorama import Fore,init
from aiohttp import AsyncResolver, ClientSession, TCPConnector
import config
import socket

init(autoreset=True)
intents = discord.Intents.default()
intents.members = True

os.environ["JISHAKU_HIDE"] = "True"

extensions = [
'cogs.admin',
'cogs.error',
'cogs.events',
'cogs.commands',
'cogs.tags',
'jishaku'
]

colors = [
    0xFFFFFF,#"WHITE" 
    0x1ABC9C,#"AQUA" 
    0x2ECC71,#"GREEN" 
    0x3498DB,#"BLUE" 
    0x9B59B6,#"PURPLE" 
    0xE91E63,#"LUMINOUS_VIVID_PINK" 
    0xF1C40F,#"GOLD"
    0xE67E22,#"ORANGE"
    0xE74C3C,#"RED"
    0x34495E,#"NAVY": 
    0x11806A,#"DARK_AQUA"
    0x1F8B4C,#"DARK_GREEN"
    0x206694,#"DARK_BLUE"
    0x71368A,#"DARK_PURPLE"
    0xAD1457,#"DARK_VIVID_PINK"
    0xC27C0E,#"DARK_GOLD"
    0xA84300,#"DARK_ORANGE"
    0x992D22,#"DARK_RED"
    0x2C3E50,#"DARK_NAVY"
]
random_color = random.choice(colors)

class IronMan(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix='!',
            intents=intents,
            strip_after_prefix=True,
            case_insensitive=True,
            chunk_guilds_at_startup=False,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, replied_user=True, users=True),
            activity=discord.Activity(type=discord.ActivityType.listening, name="to !help"),
            fetch_offline_members=True,
            help_command = HelpCommand(),
            **kwargs,
        )
        self.OWNER = 749550694469599233
        self.color = 0x73b504
        self.random_colors = random_color
        self.persistent_views_added = False
        for extension in extensions:
            try:
                self.load_extension(extension)
                print(Fore.GREEN + f"{extension} was loaded successfully!")
            except Exception as e:
                tb = traceback.format_exception(type(e), e, e.__traceback__)
                tbe = "".join(tb) + ""
                print(Fore.RED + f"[WARNING] Could not load extension {extension}: {tbe}")



    async def process_commands(self, message):
        ctx = await self.get_context(message,cls=context.Context)#

        await self.invoke(ctx)

    async def on_ready(self):
        if not self.persistent_views_added:
            

            self.add_view(SelfRoles(), message_id=887550744583110698)

            self.persistent_views_added = True

bot = IronMan()

@bot.command(hidden=True)
@commands.is_owner()
async def licog(ctx):
    await ctx.send(extensions)

async def create_db_pool():
    bot.db = await asyncpg.create_pool(database=config.postgresqldb, 
    user=config.postgresqlusername, 
    password=config.postgresqlpass,
    host=config.postgresqlhost)
    print(Fore.RED+'-------------------------------------')
    print(Fore.GREEN + 'Conected With Databse')
bot.loop.create_task(create_db_pool())

@bot.before_invoke
async def bot_before_invoke(ctx):
    if ctx.guild is not None:
        if not ctx.guild.chunked:
            await ctx.guild.chunk()

if __name__ == "__main__":
    bot.run(config.token)

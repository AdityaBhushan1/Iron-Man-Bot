import discord
from discord.ext import commands
import json
import requests
import mystbin
import unicodedata
import typing as t
from urllib.parse import quote_plus
import re
import aiohttp
import random
from.utils.replies import *
import io
import zlib
from .utils import fuzzy
import os

class SphinxObjectFileReader:
    # Inspired by Sphinx's InventoryFileReader
    BUFSIZE = 16 * 1024

    def __init__(self, buffer):
        self.stream = io.BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode('utf-8')

    def skipline(self):
        self.stream.readline()

    def read_compressed_chunks(self):
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b''
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b'\n')
            while pos != -1:
                yield buf[:pos].decode('utf-8')
                buf = buf[pos + 1:]
                pos = buf.find(b'\n')

ERROR_MESSAGE = f"""
Unknown cheat sheet. Please try to reformulate your query.

**Examples**:
```md
*cht read json
*cht hello world
*cht lambda
```
"""

URL = 'https://cheat.sh/python/{search}'
ESCAPE_TT = str.maketrans({"`": "\\`"})
ANSI_RE = re.compile(r"\x1b\[.*?m")
# We need to pass headers as curl otherwise it would default to aiohttp which would return raw html.
HEADERS = {'User-Agent': 'curl/7.68.0'}

class Commands(commands.Cog, name='Commands'):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.command()
    async def source(self, ctx):
        """yes, I am open-souce"""
        await ctx.send("<https://github.com/TierGamerpy/Iron-Man-Bot>")


    @commands.command(aliases=['r_api'])
    async def request_api(self, ctx,*,url):
        try:
            res = requests.get(url)
            res = json.loads(res.text)
            res = json.dumps(res, indent=4)
            if len(res) > 1024:
                mystbin_client = mystbin.Client()
                paste = await mystbin_client.post(res)
                em = discord.Embed(
                    description=f'The Data Is More Than discord Character limt So I HAve Posted It On BIN \n [Click Me To See]({str(paste)})')
                await ctx.send(embed=em)
            else:
                embed = discord.Embed(
                    title=f"GET Request to {url}", color=ctx.author.color)
                embed.add_field(
                    name="Output", value=f"```json\n{res}\n```", inline=False)
                embed.set_footer(
                    text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
        except:
            await ctx.send(f'Sorry Could Not Find Any Thing For `{url}`')

    @commands.command()
    async def pypi(self, ctx, *, args):
        try:
            api = f'https://pypi.org/pypi/{args}/json'
            json_data = requests.get(api).json()
            author = json_data['info']['author']
            author_email = json_data['info']['author_email']
            docs_url = json_data['info']['docs_url']
            download_url = json_data['info']['download_url']
            license = json_data['info']['license']
            name = json_data['info']['name']
            package_url = json_data['info']['package_url']

            version = json_data['info']['version']
            if author == '':
                author = 'N/A'
            if author_email == '':
                author_email = 'N/A'
            if docs_url == 'null':
                docs_url = 'N/A'
            if download_url == '':
                download_url = 'N/A'
            if license == '':
                license = 'N/A'
            if package_url == '':
                package_url = 'N/A'

            em = discord.Embed(
                title=f'**{name}**', color=ctx.author.color, inline=True)
            em.add_field(name=f'**Author Name:**', value=author)
            em.add_field(name=f'**Author Email:**', value=author_email)
            em.add_field(name=f'**Version**', value=version)
            em.add_field(name=f'**Documentation:**', value=docs_url)
            em.add_field(name=f'**Download Link:**', value=download_url)
            em.add_field(name=f'**License:**', value=license)
            em.add_field(name=f'**Pacakage URL:**', value=package_url)

            await ctx.send(embed=em)
        except:
            await ctx.send(f'Cannot find anything for `{args}`')


    # @commands.command()

    @commands.command()
    async def charinfo(self, ctx, *, characters: str):
        """Shows you information about a number of characters.

        Only up to 25 characters at a time.
        """

        def to_string(c):
            digit = f'{ord(c):x}'
            name = unicodedata.name(c, 'Name not found.')
            return f'`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'
        msg = '\n'.join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send('Output too long to display.')
        await ctx.send(msg)

    @staticmethod
    def fmt_error_embed() -> discord.Embed:
        """
        Format the Error Embed.

        If the cht.sh search returned 404, overwrite it to send a custom error embed.
        link -> https://github.com/chubin/cheat.sh/issues/198
        """
        embed = discord.Embed(
            title=random.choice(ERROR_REPLIES),
            description=ERROR_MESSAGE,
            colour=0x4ca64c
        )
        return embed

    def result_fmt(self, url: str, body_text: str) -> t.Tuple[bool, t.Union[str, discord.Embed]]:
        """Format Result."""
        if body_text.startswith("#  404 NOT FOUND"):
            embed = self.fmt_error_embed()
            return True, embed

        body_space = min(1986 - len(url), 1000)

        if len(body_text) > body_space:
            description = (f"**Result Of cht.sh**\n"
                           f"```python\n{body_text[:body_space]}\n"
                           f"... (truncated - too many lines)```\n"
                           f"Full results: {url} ")
        else:
            description = (f"**Result Of cht.sh**\n"
                           f"```python\n{body_text}```\n"
                           f"{url}")
        return False, description

    @commands.command(aliases=("cht.sh", "cheatsheet", "cheat-sheet", "cht"),)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def cheat_sheet(self, ctx, *search_terms: str) -> None:
        """
        Search cheat.sh.

        Gets a post from https://cheat.sh/python/ by default.
        Usage:
        --> .cht read json
        """
        async with ctx.typing():
            search_string = quote_plus(" ".join(search_terms))
            self.bot.session = aiohttp.ClientSession()
            async with self.bot.session.get(
                    URL.format(search=search_string), headers=HEADERS
            ) as response:
                result = ANSI_RE.sub("", await response.text()).translate(ESCAPE_TT)

            is_embed, description = self.result_fmt(
                URL.format(search=search_string),
                result
            )
            if is_embed:
                await ctx.send(embed=description)
            else:
                await ctx.send(content=description)

    def parse_object_inv(self, stream, url):
        # key: URL
        # n.b.: key doesn't have `discord` or `discord.ext.commands` namespaces
        result = {}

        # first line is version info
        inv_version = stream.readline().rstrip()

        if inv_version != '# Sphinx inventory version 2':
            raise RuntimeError('Invalid objects.inv file version.')

        # next line is "# Project: <name>"
        # then after that is "# Version: <version>"
        projname = stream.readline().rstrip()[11:]
        version = stream.readline().rstrip()[11:]

        # next line says if it's a zlib header
        line = stream.readline()
        if 'zlib' not in line:
            raise RuntimeError('Invalid objects.inv file, not z-lib compatible.')

        # This code mostly comes from the Sphinx repository.
        entry_regex = re.compile(r'(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)')
        for line in stream.read_compressed_lines():
            match = entry_regex.match(line.rstrip())
            if not match:
                continue

            name, directive, prio, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(':')
            if directive == 'py:module' and name in result:
                # From the Sphinx Repository:
                # due to a bug in 1.1 and below,
                # two inventory entries are created
                # for Python modules, and the first
                # one is correct
                continue

            # Most documentation pages have a label
            if directive == 'std:doc':
                subdirective = 'label'

            if location.endswith('$'):
                location = location[:-1] + name

            key = name if dispname == '-' else dispname
            prefix = f'{subdirective}:' if domain == 'std' else ''

            if projname == 'discord.py':
                key = key.replace('discord.ext.commands.', '').replace('discord.', '')

            result[f'{prefix}{key}'] = os.path.join(url, location)

        return result

    async def build_rtfm_lookup_table(self, page_types):
        cache = {}
        for key, page in page_types.items():
            sub = cache[key] = {}
            self.bot.session = aiohttp.ClientSession()
            async with self.bot.session.get(page + '/objects.inv') as resp:
                if resp.status != 200:
                    raise RuntimeError('Cannot build rtfm lookup table, try again later.')

                stream = SphinxObjectFileReader(await resp.read())
                cache[key] = self.parse_object_inv(stream, page)

        self._rtfm_cache = cache

    async def do_rtfm(self,ctx,key,obj):
        page_types = {
            'latest': 'https://discordpy.readthedocs.io/en/latest',
            'python': 'https://docs.python.org/3',
            "master": "https://discordpy.readthedocs.io/en/master"
        }

        if obj is None:
            await ctx.send(page_types[key])
            return
        
        if not hasattr(self, '_rtfm_cache'):
            await ctx.trigger_typing()
            await self.build_rtfm_lookup_table(page_types)

        obj = re.sub(r'^(?:discord\.(?:ext\.)?)?(?:commands\.)?(.+)', r'\1', obj)

        if key.startswith('latest'):
            q = obj.lower()
            for name in dir(discord.abc.Messageable):
                if name[0] == '_':
                    continue
                if q == name:
                    obj = f'abc.Messageable.{name}'
                    break

        cache = list(self._rtfm_cache[key].items())
        def transform(tup):
            return tup[0]

        matches = fuzzy.finder(obj, cache, key=lambda t: t[0], lazy=False)[:12]

        e = discord.Embed(colour=discord.Colour.green(),title=f"Here are some results for `{obj}` :")
        if len(matches) == 0:
            return await ctx.send('Could not find anything. Sorry.')

        e.description = '\n'.join(f'[`{key}`]({url})' for key, url in matches)
        await ctx.send(embed=e)

    def transform_rtfm_language_key(self, ctx, prefix):
        if ctx.guild is not None:
            #                             日本語 category
            if ctx.channel.category_id == 490287576670928914:
                return prefix + '-jp'
            #                    d.py unofficial JP   Discord Bot Portal JP
            elif ctx.guild.id in (463986890190749698, 494911447420108820):
                return prefix + '-jp'
        return prefix

    @commands.group(aliases=['rtfd'], invoke_without_command=True)
    async def rtfm(self, ctx, *, obj: str = None):
        key = self.transform_rtfm_language_key(ctx, 'latest')
        await self.do_rtfm(ctx, key, obj)

    @rtfm.command(name='python', aliases=['py'])
    async def rtfm_python(self, ctx, *, obj: str = None):
        key = self.transform_rtfm_language_key(ctx, 'python')
        await self.do_rtfm(ctx, key, obj)
    
    @rtfm.command(name="master", aliases=["2.0"])
    async def rtfm_master(self, ctx, *, obj: str = None):
        """Gives you a documentation link for a discord.py entity (master branch)"""
        await self.do_rtfm(ctx, "master", obj)
        

def setup(bot):
    bot.add_cog(Commands(bot))

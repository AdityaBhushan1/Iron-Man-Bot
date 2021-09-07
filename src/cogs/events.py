from discord.ext import commands
import discord,re
from colorama import Fore
import typing as t


WEBHOOK_URL_RE = re.compile(r"((?:https?://)?discord(?:app)?\.com/api/webhooks/\d+/)\S+/?", re.IGNORECASE)

Webhook_ALERT_MESSAGE_TEMPLATE = (
    "{user}, looks like you posted a Discord webhook URL. Therefore, your "
    "message has been removed. Your webhook may have been **compromised** so "
    "please re-create the webhook **immediately**. If you believe this was a "
    "mistake, please let us know."
)
token_DELETION_MESSAGE_TEMPLATE = (
    "Hey {mention}! I noticed you posted a seemingly valid Discord API "
    "token in your message and have removed your message. "
    "This means that your token has been **compromised**. "
    "Please change your token **immediately** at: "
    "<https://discordapp.com/developers/applications/me>\n\n"
    "Feel free to re-post it with the token removed. "
    "If you believe this was a mistake, please let us know!"
)
DISCORD_EPOCH = 1_420_070_400
TOKEN_EPOCH = 1_293_840_000

# Three parts delimited by dots: user ID, creation timestamp, HMAC.
# The HMAC isn't parsed further, but it's in the regex to ensure it at least exists in the string.
# Each part only matches base64 URL-safe characters.
# Padding has never been observed, but the padding character '=' is matched just in case.
TOKEN_RE = re.compile(r"([\w\-=]+)\.([\w\-=]+)\.([\w\-=]+)", re.ASCII)

class Token(t.NamedTuple):
    """A Discord Bot token."""

    user_id: str
    timestamp: str
    hmac: str

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def webhook_delete_and_respond(self, msg: discord.Message, redacted_url: str) -> None:
        """Delete `msg` and send a warning that it contained the Discord webhook `redacted_url`."""
        # Don't log this, due internal delete, not by user. Will make different entry.
        # self.mod_log.ignore(Event.message_delete, msg.id)

        try:
            await msg.delete()
        except discord.NotFound:
            return

        await msg.channel.send(Webhook_ALERT_MESSAGE_TEMPLATE.format(user=msg.author.mention))

    @commands.Cog.listener()
    async def on_ready(self):
        #     await webhook.send(embed=e)
        print(Fore.RED+f"-------------------------------------")
        print(Fore.GREEN + f"Logging In...........................")
        print(Fore.GREEN + f"Logged In as: {self.bot.user.name}({self.bot.user.id})")
        print(Fore.GREEN + f"Connected Guilds:", len(self.bot.guilds))
        print(Fore.GREEN + f"Connected Users", len(self.bot.users))
        print(Fore.RED+f"-------------------------------------")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 782868622241955851:
            channel = self.bot.get_channel(782879729669636117)
            em = discord.Embed(title = f'**Aquatrix-Development**',description = f'Hello **{member.name}**, Welcome to **__Aquatrix-Development Support Server__**',color = self.bot.random_colors)
            em.set_thumbnail(url = member.avatar.url)
            # em.set_footer(text='Powered By Tea Bot')
            await channel.send(content = member.mention,embed=em)

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message) -> None:
        """Check if a Discord webhook URL is in `message`."""
        # Ignore DMs; can't delete messages in there anyway.
        if not msg.guild or msg.author.bot:
            return

        matches = WEBHOOK_URL_RE.search(msg.content)
        if matches:
            await self.webhook_delete_and_respond(msg, matches[1] + "xxx")
        found_token = self.find_token_in_message(msg)
        if found_token:
            await self.token_take_action(msg, found_token)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        """Check if a Discord webhook URL is in the edited message `after`."""
        await self.on_message(after)

    async def token_take_action(self, msg: discord.Message, found_token: Token) -> None:
        """Remove the `msg` containing the `found_token` and send a mod log message."""
        try:
            await msg.delete()
        except discord.NotFound:
            return

        await msg.channel.send(token_DELETION_MESSAGE_TEMPLATE.format(mention=msg.author.mention))

    @classmethod
    def find_token_in_message(cls, msg: discord.Message) -> t.Optional[Token]:
        """Return a seemingly valid token found in `msg` or `None` if no token is found."""
        # Use finditer rather than search to guard against method calls prematurely returning the
        # token check (e.g. `message.channel.send` also matches our token pattern)
        for match in TOKEN_RE.finditer(msg.content):
            token = Token(*match.groups())
            if (
                (cls.extract_user_id(token.user_id) is not None)
                and cls.is_valid_timestamp(token.timestamp)
                and cls.is_maybe_valid_hmac(token.hmac)
            ):
                # Short-circuit on first match
                return token

        # No matching substring
        return


def setup(bot):
    bot.add_cog(Events(bot))

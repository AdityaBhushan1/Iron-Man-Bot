from difflib import get_close_matches
from discord.ext import commands
import discord


class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(
            command_attrs={
                "help": "Shows help about the bot, a command, or a category",
            },
            verify_checks=False,
        )

    async def send_bot_help(self, mapping):
        ctx = self.context
        cats = []

        for cog, cmds in mapping.items():
            if cog and await self.filter_commands(cmds, sort=True):
                cats.append(cog)

        embed = discord.Embed(color=discord.Color(0x73b504))
        for idx in cats:
            embed.add_field(
                inline=False,
                name=idx.qualified_name.title(),
                value=", ".join(map(lambda x: f"`{x}`", filter(lambda x: not x.hidden, idx.get_commands()))),
            )
        await ctx.send(embed=embed)

    async def command_not_found(self, string: str):
        message = f"Could not find the `{string}` command. "
        commands_list = [str(cmd) for cmd in self.context.bot.walk_commands()]

        if dym := "\n".join(get_close_matches(string, commands_list)):
            message += f"Did you mean...\n{dym}"

        return message

    async def send_command_help(self, command):
        embed = self.common_command_formatting(command)
        await self.context.send(embed=embed)

    def common_command_formatting(self, command):
        embed = discord.Embed(color=0x73b504)
        embed.title = command.qualified_name

        if command.description:
            embed.description = f"{command.description}\n\n{command.help}"
        else:
            embed.description = command.help or "No help found..."
        embed.add_field(name="**Usage** ", value=f"`{self.get_command_signature(command)}`")

        return embed


# class HelpCog(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.old_help_command = bot.help_command
#         bot.help_command = HelpCommand()
#         bot.help_command.cog = self
        

#     def cog_unload(self):
#         self.bot.help_command = self.old_help_command


# def setup(bot):
#     bot.add_cog(HelpCog(bot))


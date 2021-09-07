import discord


class SelfRoles(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.credo_updates_role = 814327916057591808
        self.testers = 806022784002162739
        self.events = 823911554441019483

    @discord.ui.button(style=discord.ButtonStyle.blurple, custom_id="credo_updates", label="Credo-Updates", row=1)
    async def credo_updates(self, button: discord.Button, interaction: discord.Interaction):
        if self.credo_updates_role in (role.id for role in interaction.user.roles):
            await interaction.user.remove_roles(discord.Object(id=self.credo_updates_role))
            return await interaction.response.send_message("Credo-Updates role removed.", ephemeral=True)

        await interaction.user.add_roles(discord.Object(id=self.credo_updates_role))
        return await interaction.response.send_message("Credo-Updates role added.", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.blurple, custom_id="events", label="Events", row=1)
    async def aquatrix_events(self, button: discord.Button, interaction: discord.Interaction):
        if self.events in (role.id for role in interaction.user.roles):
            await interaction.user.remove_roles(discord.Object(id=self.events))
            return await interaction.response.send_message("Events role removed.", ephemeral=True)

        await interaction.user.add_roles(discord.Object(id=self.events))
        return await interaction.response.send_message("Events role  added.", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.blurple, custom_id="black", label="Testers", row=1)
    async def credo_testers(self, button: discord.Button, interaction: discord.Interaction):
        if self.testers in (role.id for role in interaction.user.roles):
            await interaction.user.remove_roles(discord.Object(id=self.testers))
            return await interaction.response.send_message("Testers role removed.", ephemeral=True)

        await interaction.user.add_roles(discord.Object(id=self.testers))
        return await interaction.response.send_message("Testers role added.", ephemeral=True)
import asyncio
import discord
import os
from dotenv import load_dotenv

from src.database import DatabaseRepository

load_dotenv()
bot = discord.Bot()
TOKEN = str(os.getenv("DISCORD_BOT_TOKEN"))

db = DatabaseRepository()


class RegisterModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(
            discord.ui.InputText(label="What ships or chars do you wanna receive?")
        )
        self.add_item(
            discord.ui.InputText(
                label="What tropes, setups or vibes do you like?",
                style=discord.InputTextStyle.long,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Is there any topic you want to avoid?",
                style=discord.InputTextStyle.long,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild_id
        user = interaction.user.id
        ship_list = self.children[0].value or ""
        yums = self.children[1].value or ""
        yucks = self.children[2].value or ""

        await interaction.response.defer(ephemeral=True)

        registration = await asyncio.to_thread(
            lambda: db.get_registration_by_pk(user_id=user, guild_id=guild)
        )

        if registration.data and len(registration.data) > 0:
            await interaction.followup.send(
                "You are already registered for the Secret Santa!", ephemeral=True
            )
            return
        else:
            await asyncio.to_thread(
                lambda: db.save_registration(
                    user_id=user,
                    guild_id=guild,
                    data={
                        "yucks": yucks,
                        "yums": yums,
                        "ship_list": ship_list,
                    },
                )
            )

            embed = discord.Embed(title="Modal Results")
            embed.add_field(
                name="What characters or ships are you interested in receiving fan works for?",
                value=ship_list,
            )
            embed.add_field(
                name="What tropes, setups or vibes do you like?", value=yums
            )
            embed.add_field(
                name="Is there any topic or theme you want to avoid?", value=yucks
            )

            await interaction.followup.send(
                "Welcome to the Secret Santa!", ephemeral=True
            )


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


@bot.slash_command(name="register", description="Register in the server's Secret Santa")
async def register(ctx: discord.ApplicationContext):
    modal = RegisterModal(title="Laboratory Secret Santa Inscription Form")
    await ctx.send_modal(modal)


bot.run(TOKEN)

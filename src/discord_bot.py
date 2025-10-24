import discord
import os

from dotenv import load_dotenv

load_dotenv()
bot = discord.Bot()
TOKEN = str(os.getenv('DISCORD_BOT_TOKEN'))

class RegisterModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(
            discord.ui.InputText(label="What ships or chars do you wanna receive?")
        )
        self.add_item(
            discord.ui.InputText(
                label="What tropes, setups or vibes do you like?",
                style=discord.InputTextStyle.long
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Is there any topic you want to avoid?",
                style=discord.InputTextStyle.long
            )
        )

    async def callback(self, interaction: discord.Interaction):
        print(self.children)
        embed = discord.Embed(title="Modal Results")
        embed.add_field(
            name="What characters or ships are you interested in receiving fan works for?",
            value=self.children[0].value
        )
        embed.add_field(name="What tropes, setups or vibes do you like?", value=self.children[1].value)
        embed.add_field(name="Is there any topic or theme you want to avoid?", value=self.children[2].value)
        await interaction.response.send_message(embeds=[embed])

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="register", description="Register in the server's Secret Santa")
async def register(ctx: discord.ApplicationContext):
    modal = RegisterModal(title="Laboratory Secret Santa Inscription Form")
    await ctx.send_modal(modal)


bot.run(TOKEN)
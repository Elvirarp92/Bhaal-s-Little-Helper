import asyncio
import discord
import os

from discord.ext import commands
from dotenv import load_dotenv

from src.schemas import AssignmentWithReceiverInfo
from src.sorter import SecretSantaSorter
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


class EditModal(discord.ui.Modal):
    def __init__(self, initial_values, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(
            discord.ui.InputText(
                label="What ships or chars do you wanna receive?",
                value=initial_values.get("ship_list", ""),
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="What tropes, setups or vibes do you like?",
                value=initial_values.get("yums", ""),
                style=discord.InputTextStyle.long,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Is there any topic you want to avoid?",
                value=initial_values.get("yucks", ""),
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

        await asyncio.to_thread(
            lambda: db.update_registration(
                user_id=user,
                guild_id=guild,
                data={"yucks": yucks, "yums": yums, "ship_list": ship_list},
            )
        )

        await interaction.followup.send(
            "Your registration has been updated.", ephemeral=True
        )


class DeleteModal(discord.ui.Modal):
    confirmation_phrase = "DELETE"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(
            discord.ui.InputText(
                label=f"Type {self.confirmation_phrase} to confirm deletion",
                placeholder="Type the confirmation phrase exactly",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild_id
        user = interaction.user.id
        value = (self.children[0].value or "").strip()
        await interaction.response.defer(ephemeral=True)

        if value != self.confirmation_phrase:
            await interaction.followup.send(
                "Confirmation phrase didn't match!", ephemeral=True
            )
            return

        await asyncio.to_thread(
            lambda: db.delete_registration(
                user_id=user,
                guild_id=guild,
            )
        )

        await interaction.followup.send(
            "Your registration has been deleted.", ephemeral=True
        )


async def send_assignment_id(assignment: AssignmentWithReceiverInfo):
    giver_id = int(assignment["giver_discord_id"])
    giver = await bot.fetch_user(giver_id)
    receiver_id = int(assignment["receiver_discord_id"])
    receiver = await bot.fetch_user(receiver_id)
    if giver:
        if receiver:
            try:
                await giver.send(
                    "# HO, HO, HO, MORTAL! \n"
                    f"## You've been assigned {receiver.mention} as a Secret Santa recipient!"
                    f"\n\nHere are their preferences:\n"
                    f"**Ships/Characters:** {assignment['receiver_ship_list']}\n"
                    f"**Likes (Yums):** {assignment['receiver_yums']}\n"
                    f"**Dislikes (Yucks):** {assignment['receiver_yucks']}\n\n"
                    "Don't forget to **keep it a secret until 2026/01/06** and have a dead good time preparing their gift!"
                )
            except Exception as e:
                print(f"Failed to send DM to {giver_id}: {e}")
        else:
            print(f"Receiver with ID {receiver_id} not found.")
    else:
        print(f"User with ID {giver_id} not found.")


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


@bot.slash_command(name="register", description="Register in the server's Secret Santa")
async def register(ctx: discord.ApplicationContext):
    modal = RegisterModal(title="Laboratory Secret Santa Inscription Form")
    await ctx.send_modal(modal)


@bot.slash_command(name="edit", description="Edit your Secret Santa registration")
async def edit(ctx: discord.ApplicationContext):
    guild = ctx.guild_id
    user = ctx.user.id

    registration = await asyncio.to_thread(
        lambda: db.get_registration_by_pk(user_id=user, guild_id=guild)
    )

    if not getattr(registration, "data", None) or len(registration.data) == 0:
        await ctx.respond(
            "You are not registered yet! Please register (/register) first.",
            ephemeral=True,
        )
        return

    stored = (
        registration.data[0]
        if isinstance(registration.data, list)
        else registration.data
    )
    initial_values = {
        "ship_list": stored.get("ship_list", "") if isinstance(stored, dict) else "",
        "yums": stored.get("yums", "") if isinstance(stored, dict) else "",
        "yucks": stored.get("yucks", "") if isinstance(stored, dict) else "",
    }

    modal = EditModal(
        title="Edit your Secret Santa Registration", initial_values=initial_values
    )
    await ctx.send_modal(modal)


@bot.slash_command(name="delete", description="Delete your Secret Santa registration")
async def delete(ctx: discord.ApplicationContext):
    guild = ctx.guild_id
    user = ctx.user.id

    # fetch registration before showing modal
    registration = await asyncio.to_thread(
        lambda: db.get_registration_by_pk(user_id=user, guild_id=guild)
    )
    if not getattr(registration, "data", None) or len(registration.data) == 0:
        await ctx.respond("You are not registered!", ephemeral=True)
        return

    modal = DeleteModal(title="Delete your Secret Santa Registration")
    await ctx.send_modal(modal)


@bot.slash_command(name="sort", description="Sort Secret Santa assignments")
@commands.has_permissions(administrator=True)
async def sort(ctx: discord.ApplicationContext):
    await ctx.defer(ephemeral=True)

    guild = ctx.guild_id
    sorter = SecretSantaSorter(db_repository=db, guild_id=guild)
    assignments = await asyncio.to_thread(lambda: sorter.perform_sorting())

    await asyncio.gather(*(send_assignment_id(a) for a in assignments))

    if len(assignments) == 0:
        await ctx.respond(
            "No participants registered for Secret Santa.", ephemeral=True
        )
        return

    await ctx.respond(
        f"Sorted {len(assignments)} participants for Secret Santa!", ephemeral=True
    )


bot.run(TOKEN)

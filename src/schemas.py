from typing import TypedDict


class DiscordRegistrationForm(TypedDict):
    yucks: str
    yums: str
    ship_list: str


class UserRegistration(DiscordRegistrationForm):
    discord_id: str
    guild_id: str


class Assignment(TypedDict):
    giver_discord_id: str
    receiver_discord_id: str
    guild_id: str


class AssignmentWithReceiverInfo(Assignment):
    receiver_yucks: str
    receiver_yums: str
    receiver_ship_list: str

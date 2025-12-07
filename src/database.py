import os

from supabase import Client, create_client

from src.schemas import Registration


class DatabaseRepository:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_SECRET")  #
        self.registration_table: str = "users"
        self.client: Client = create_client(url, key)

    def save_registration(self, user_id: int, guild_id: int, data: Registration):
        return (
            self.client.table(self.registration_table)
            .insert(
                {
                    "discord_id": user_id,
                    "guild_id": guild_id,
                    "yucks": data["yucks"],
                    "yums": data["yums"],
                    "ship_list": data["ship_list"],
                }
            )
            .execute()
        )

    def get_registration_by_pk(self, user_id: int, guild_id: int):
        return (
            self.client.table(self.registration_table)
            .select("*")
            .eq("discord_id", user_id)
            .eq("guild_id", guild_id)
            .execute()
        )

    def update_registration(self, user_id: int, guild_id: int, data: Registration):
        return (
            self.client.table(self.registration_table)
            .update(
                {
                    "yucks": data["yucks"],
                    "yums": data["yums"],
                    "ship_list": data["ship_list"],
                }
            )
            .eq("discord_id", user_id)
            .eq("guild_id", guild_id)
            .execute()
        )

    def delete_registration(self, user_id: int, guild_id: int):
        pass

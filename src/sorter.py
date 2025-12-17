import random

from src.database import DatabaseRepository
from src.schemas import UserRegistration, Assignment, AssignmentWithReceiverInfo


class SecretSantaSorter:
    def __init__(self, db_repository: DatabaseRepository, guild_id: int):
        self.db_repository = db_repository
        self.guild_id = guild_id
        self.participants: list[UserRegistration] = []
        self.assignments: list[Assignment] = []
        self.assignments_with_receiver_info: list[AssignmentWithReceiverInfo] = []

    def _sort_participants(
        self,
    ) -> tuple[list[Assignment], list[AssignmentWithReceiverInfo]]:
        shuffled_participants: list[UserRegistration] = random.sample(
            self.participants, len(self.participants)
        )
        assignments: list[Assignment] = []
        assignments_with_receiver_info = []

        for index, participant in enumerate(shuffled_participants):
            receiver_index = (index + 1) % len(self.participants)
            receiver = shuffled_participants[receiver_index]
            assignment: Assignment = {
                "giver_discord_id": participant["discord_id"],
                "receiver_discord_id": receiver["discord_id"],
                "guild_id": participant["guild_id"],
            }
            assignment_with_receiver_info = {
                "giver_discord_id": participant["discord_id"],
                "receiver_discord_id": receiver["discord_id"],
                "guild_id": participant["guild_id"],
                "receiver_yucks": receiver["yucks"],
                "receiver_yums": receiver["yums"],
                "receiver_ship_list": receiver["ship_list"],
            }
            assignments.append(assignment)
            assignments_with_receiver_info.append(assignment_with_receiver_info)

        return assignments, assignments_with_receiver_info

    def _fetch_participants(self) -> list[UserRegistration]:
        return self.db_repository.get_registrations_by_guild(self.guild_id).data

    def _save_assignments(self):
        self.db_repository.save_assignments(self.assignments)

    def perform_sorting(self) -> list[AssignmentWithReceiverInfo]:
        self.participants = self._fetch_participants()
        self.assignments, self.assignments_with_receiver_info = (
            self._sort_participants()
        )
        self._save_assignments()

        return self.assignments_with_receiver_info

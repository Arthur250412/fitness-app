from __future__ import annotations

from app.models import UserState


class InMemoryStore:
    def __init__(self) -> None:
        self.users: dict[str, UserState] = {}

    def save(self, user: UserState) -> None:
        self.users[user.profile.user_id] = user

    def get(self, user_id: str) -> UserState:
        if user_id not in self.users:
            raise KeyError(f"user {user_id} not found")
        return self.users[user_id]

from __future__ import annotations

import math
from datetime import date

from app.models import Achievement, GamificationState, WeeklyMission


class GamificationEngine:
    def update(self, state: GamificationState, completed: int, total: int, checkin_day: date) -> GamificationState:
        total = max(1, total)
        ratio = completed / total
        gained_xp = int(20 + 80 * ratio)
        state.xp += gained_xp
        state.level = math.floor(math.sqrt(state.xp / 100)) + 1

        if ratio >= 0.7:
            state.weekly_streak += 1
        else:
            state.weekly_streak = max(0, state.weekly_streak - 1)

        self._unlock_achievements(state, checkin_day)
        self._ensure_missions(state)
        self._update_missions(state, completed)
        return state

    def _unlock_achievements(self, state: GamificationState, checkin_day: date) -> None:
        existing = {a.key for a in state.achievements}
        if state.weekly_streak >= 7 and "streak_7" not in existing:
            state.achievements.append(Achievement(key="streak_7", unlocked_at=checkin_day))
        if state.level >= 5 and "level_5" not in existing:
            state.achievements.append(Achievement(key="level_5", unlocked_at=checkin_day))

    def _ensure_missions(self, state: GamificationState) -> None:
        if not state.weekly_missions:
            state.weekly_missions = [
                WeeklyMission(title="Concluir 12 tarefas de rotina", target=12),
                WeeklyMission(title="Fazer 4 sessões de treino", target=4),
            ]

    def _update_missions(self, state: GamificationState, completed_tasks: int) -> None:
        for mission in state.weekly_missions:
            mission.progress = min(mission.target, mission.progress + completed_tasks)

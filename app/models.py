from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Goal(str, Enum):
    WEIGHT_LOSS = "emagrecimento"
    MUSCLE_GAIN = "ganho_massa"
    GENERAL_HEALTH = "saude_geral"


class ActivityLevel(str, Enum):
    SEDENTARY = "sedentario"
    LIGHT = "leve"
    MODERATE = "moderado"
    HIGH = "alto"


class Sex(str, Enum):
    FEMALE = "feminino"
    MALE = "masculino"
    OTHER = "outro"


class UserProfile(BaseModel):
    user_id: str
    age: int
    sex: Sex
    height_cm: float
    weight_kg: float
    goal: Goal
    activity_level: ActivityLevel
    dietary_restrictions: List[str] = Field(default_factory=list)
    weekly_availability_days: int = 4
    preferences: List[str] = Field(default_factory=list)


class AdaptiveRuleSet(BaseModel):
    volume_multiplier: float = 1.0
    intensity_multiplier: float = 1.0
    calorie_delta: int = 0
    simplify_nutrition: bool = False


class TrainingDayPlan(BaseModel):
    weekday: str
    focus: str
    intensity: int
    volume_sets: int
    rest_seconds: int


class MealPlan(BaseModel):
    calories: int
    protein_g: int
    carbs_g: int
    fats_g: int
    notes: List[str] = Field(default_factory=list)


class DailyTask(BaseModel):
    title: str
    kind: str
    done: bool = False


class DailyPlan(BaseModel):
    day: str
    tasks: List[DailyTask]


class WeeklyPlan(BaseModel):
    training: List[TrainingDayPlan]
    nutrition: MealPlan
    routine: List[DailyPlan]
    explanation: str


class ProgressSnapshot(BaseModel):
    day: date
    weight_kg: Optional[float] = None
    energy_score: int = 3
    performance_score: int = 3
    adherence_score: int = 3


class Achievement(BaseModel):
    key: str
    unlocked_at: date


class WeeklyMission(BaseModel):
    title: str
    target: int
    progress: int = 0


class GamificationState(BaseModel):
    xp: int = 0
    level: int = 1
    weekly_streak: int = 0
    achievements: List[Achievement] = Field(default_factory=list)
    weekly_missions: List[WeeklyMission] = Field(default_factory=list)


class UserState(BaseModel):
    profile: UserProfile
    rules: AdaptiveRuleSet
    current_plan: WeeklyPlan
    progress_history: List[ProgressSnapshot] = Field(default_factory=list)
    failures_by_weekday: Dict[str, int] = Field(default_factory=dict)
    gamification: GamificationState = Field(default_factory=GamificationState)


class OnboardingRequest(BaseModel):
    age: int
    sex: Sex
    height_cm: float
    weight_kg: float
    goal: Goal
    activity_level: ActivityLevel
    dietary_restrictions: List[str] = Field(default_factory=list)
    weekly_availability_days: int
    preferences: List[str] = Field(default_factory=list)


class CheckinRequest(BaseModel):
    day: date
    weekday: str
    tasks_completed: int
    tasks_total: int
    weight_kg: Optional[float] = None
    energy_score: int = Field(ge=1, le=5)
    performance_score: int = Field(ge=1, le=5)


class WeeklyReport(BaseModel):
    summary: str
    changes: List[str]
    consistency_score: float
    next_focus: str

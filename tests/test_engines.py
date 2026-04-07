from datetime import date, timedelta

from app.engines.analysis import AnalysisEngine
from app.engines.gamification import GamificationEngine
from app.engines.rules import RuleEngine
from app.models import (
    ActivityLevel,
    AdaptiveRuleSet,
    GamificationState,
    Goal,
    ProgressSnapshot,
    Sex,
    UserProfile,
)


def test_rule_engine_generates_non_template_plan():
    profile = UserProfile(
        user_id="u1",
        age=30,
        sex=Sex.MALE,
        height_cm=178,
        weight_kg=82,
        goal=Goal.WEIGHT_LOSS,
        activity_level=ActivityLevel.MODERATE,
        weekly_availability_days=5,
        preferences=["treino curto"],
    )
    plan = RuleEngine().generate_plan(profile, AdaptiveRuleSet())
    assert len(plan.training) == 5
    assert plan.nutrition.calories > 0
    assert any("Treino" in task.title for d in plan.routine for task in d.tasks)


def test_analysis_engine_reduces_volume_after_poor_performance():
    engine = AnalysisEngine()
    rules = AdaptiveRuleSet()
    today = date.today()
    history = [
        ProgressSnapshot(
            day=today - timedelta(days=i),
            performance_score=2,
            adherence_score=3,
            energy_score=3,
            weight_kg=80,
        )
        for i in range(5)
    ]
    updated, changes = engine.adapt_rules(history, rules)
    assert updated.volume_multiplier < 1.0
    assert changes


def test_gamification_increases_level_with_xp():
    engine = GamificationEngine()
    state = engine.update(state=GamificationState(), completed=3, total=3, checkin_day=date.today())
    assert state.xp > 0
    assert state.level >= 1

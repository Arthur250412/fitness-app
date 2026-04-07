from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, HTTPException

from app.engines.analysis import AnalysisEngine
from app.engines.gamification import GamificationEngine
from app.engines.rules import RuleEngine
from app.models import (
    AdaptiveRuleSet,
    CheckinRequest,
    OnboardingRequest,
    ProgressSnapshot,
    UserProfile,
    UserState,
    WeeklyReport,
)
from app.store import InMemoryStore

app = FastAPI(title="FitLoop AI API", version="0.1.0")
store = InMemoryStore()
rule_engine = RuleEngine()
analysis_engine = AnalysisEngine()
gamification_engine = GamificationEngine()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/onboarding")
def onboarding(payload: OnboardingRequest):
    user_id = str(uuid4())
    profile = UserProfile(user_id=user_id, **payload.model_dump())
    rules = AdaptiveRuleSet()
    plan = rule_engine.generate_plan(profile, rules)
    state = UserState(profile=profile, rules=rules, current_plan=plan)
    store.save(state)
    return {"user_id": user_id, "plan": plan, "rules": rules}


@app.get("/plan/{user_id}")
def get_plan(user_id: str):
    try:
        user = store.get(user_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"user_id": user_id, "plan": user.current_plan, "gamification": user.gamification}


@app.post("/checkin/{user_id}")
def checkin(user_id: str, payload: CheckinRequest):
    try:
        user = store.get(user_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    adherence_score = round((payload.tasks_completed / max(1, payload.tasks_total)) * 5)
    snapshot = ProgressSnapshot(
        day=payload.day,
        weight_kg=payload.weight_kg,
        energy_score=payload.energy_score,
        performance_score=payload.performance_score,
        adherence_score=adherence_score,
    )
    user.progress_history.append(snapshot)

    if adherence_score <= 2:
        user.failures_by_weekday[payload.weekday] = user.failures_by_weekday.get(payload.weekday, 0) + 1

    updated_rules, changes = analysis_engine.adapt_rules(user.progress_history, user.rules)
    user.rules = updated_rules
    user.current_plan = rule_engine.generate_plan(user.profile, user.rules)
    user.gamification = gamification_engine.update(
        user.gamification,
        completed=payload.tasks_completed,
        total=payload.tasks_total,
        checkin_day=payload.day,
    )
    store.save(user)
    return {
        "message": "Check-in recebido. Plano ajustado automaticamente.",
        "changes": changes,
        "rules": user.rules,
        "gamification": user.gamification,
    }


@app.get("/weekly-report/{user_id}", response_model=WeeklyReport)
def weekly_report(user_id: str):
    try:
        user = store.get(user_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    recent = user.progress_history[-7:]
    if not recent:
        return WeeklyReport(
            summary="Sem dados suficientes nesta semana.",
            changes=[],
            consistency_score=0.0,
            next_focus="Completar check-ins diários.",
        )

    consistency = sum(p.adherence_score for p in recent) / (len(recent) * 5)
    changes = []
    if user.rules.simplify_nutrition:
        changes.append("Nutrição simplificada para aumentar aderência.")
    if user.rules.volume_multiplier < 1.0:
        changes.append("Volume de treino reduzido para recuperação e retomada de performance.")

    problem_day = None
    if user.failures_by_weekday:
        problem_day = max(user.failures_by_weekday, key=user.failures_by_weekday.get)

    next_focus = (
        f"Reorganizar tarefas de {problem_day} com blocos menores."
        if problem_day
        else "Manter consistência e aumentar progressivamente a intensidade."
    )

    return WeeklyReport(
        summary="Você está evoluindo com um plano adaptativo focado em consistência.",
        changes=changes,
        consistency_score=round(consistency, 2),
        next_focus=next_focus,
    )

from __future__ import annotations

from app.models import (
    ActivityLevel,
    AdaptiveRuleSet,
    Goal,
    MealPlan,
    TrainingDayPlan,
    UserProfile,
    WeeklyPlan,
)


class RuleEngine:
    def generate_plan(self, profile: UserProfile, rules: AdaptiveRuleSet) -> WeeklyPlan:
        training = self._build_training(profile, rules)
        meal = self._build_meal_plan(profile, rules)
        routine = self._build_routine(training)
        explanation = (
            "Plano criado com base no seu objetivo, disponibilidade e aderência recente. "
            "Ele será ajustado automaticamente conforme seus check-ins."
        )
        return WeeklyPlan(training=training, nutrition=meal, routine=routine, explanation=explanation)

    def _build_training(self, profile: UserProfile, rules: AdaptiveRuleSet):
        base_sets_by_level = {
            ActivityLevel.SEDENTARY: 8,
            ActivityLevel.LIGHT: 10,
            ActivityLevel.MODERATE: 12,
            ActivityLevel.HIGH: 14,
        }
        base_intensity = {
            Goal.WEIGHT_LOSS: 6,
            Goal.MUSCLE_GAIN: 8,
            Goal.GENERAL_HEALTH: 7,
        }[profile.goal]

        short_pref = any("curto" in p.lower() for p in profile.preferences)
        focuses = ["força", "hipertrofia", "cardio", "mobilidade", "misto", "recuperação ativa"]
        days = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]

        plan = []
        for i in range(profile.weekly_availability_days):
            sets = int(base_sets_by_level[profile.activity_level] * rules.volume_multiplier)
            if short_pref:
                sets = max(6, sets - 2)

            intensity = max(4, min(10, int(base_intensity * rules.intensity_multiplier)))
            rest = 60 if profile.goal == Goal.WEIGHT_LOSS else 90
            plan.append(
                TrainingDayPlan(
                    weekday=days[i],
                    focus=focuses[i % len(focuses)],
                    intensity=intensity,
                    volume_sets=sets,
                    rest_seconds=rest,
                )
            )
        return plan

    def _build_meal_plan(self, profile: UserProfile, rules: AdaptiveRuleSet):
        activity_factor = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHT: 1.35,
            ActivityLevel.MODERATE: 1.5,
            ActivityLevel.HIGH: 1.7,
        }[profile.activity_level]
        tdee = int((22 * profile.weight_kg) * activity_factor)

        if profile.goal == Goal.WEIGHT_LOSS:
            calories = int(tdee * 0.85)
            protein_per_kg = 2.0
        elif profile.goal == Goal.MUSCLE_GAIN:
            calories = int(tdee * 1.10)
            protein_per_kg = 2.2
        else:
            calories = tdee
            protein_per_kg = 1.8

        calories += rules.calorie_delta
        protein = int(profile.weight_kg * protein_per_kg)
        fats = int((calories * 0.25) / 9)
        carbs = int((calories - (protein * 4 + fats * 9)) / 4)

        notes = []
        if profile.dietary_restrictions:
            notes.append("Restrições consideradas: " + ", ".join(profile.dietary_restrictions))
        if rules.simplify_nutrition:
            notes.append("Plano simplificado: refeições repetíveis e preparo rápido.")

        return MealPlan(
            calories=calories,
            protein_g=protein,
            carbs_g=max(50, carbs),
            fats_g=max(30, fats),
            notes=notes,
        )

    def _build_routine(self, training):
        from app.models import DailyPlan, DailyTask

        routine = []
        for t in training:
            tasks = [
                DailyTask(title=f"Treino {t.focus}", kind="treino"),
                DailyTask(title="Seguir plano alimentar", kind="refeicao"),
                DailyTask(title="Beber 2L de água", kind="habito"),
            ]
            routine.append(DailyPlan(day=t.weekday, tasks=tasks))
        return routine

from __future__ import annotations

from statistics import mean

from app.models import AdaptiveRuleSet, ProgressSnapshot


class AnalysisEngine:
    def adapt_rules(self, history: list[ProgressSnapshot], current_rules: AdaptiveRuleSet) -> tuple[AdaptiveRuleSet, list[str]]:
        rules = current_rules.model_copy(deep=True)
        changes: list[str] = []

        if len(history) >= 5:
            recent_perf = [h.performance_score for h in history[-5:]]
            if all(score <= 2 for score in recent_perf):
                rules.volume_multiplier = max(0.75, rules.volume_multiplier - 0.1)
                changes.append("Reduzi o volume do treino porque sua performance caiu por 5 dias seguidos.")

        if len(history) >= 7:
            recent_adherence = [h.adherence_score for h in history[-7:]]
            if mean(recent_adherence) < 2.5:
                rules.simplify_nutrition = True
                changes.append("Simplifiquei sua dieta porque sua aderência ficou baixa na última semana.")

        if len(history) >= 14:
            recent_weights = [h.weight_kg for h in history[-14:] if h.weight_kg is not None]
            if len(recent_weights) >= 8 and (max(recent_weights) - min(recent_weights) < 0.4):
                rules.calorie_delta -= 120
                changes.append("Ajustei suas calorias após identificar estagnação de peso.")

        return rules, changes

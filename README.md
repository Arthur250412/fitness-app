# FitLoop AI — B2C Fitness & Saúde Personalizada

FitLoop AI é um MVP funcional de um aplicativo B2C de fitness e saúde que **gera e evolui planos personalizados do zero**, sem templates fixos. O sistema combina treino, dieta, rotina diária, análise contínua de progresso e gamificação para maximizar retenção e resultado real.

## 1) Visão geral do produto

### Proposta de valor
- Plano vivo que se adapta ao usuário (não o contrário).
- Consistência > perfeição: o sistema simplifica quando a aderência cai.
- Feedback diário curto e explicações claras sobre cada ajuste.

### Fluxo de uso
1. Usuário faz onboarding inteligente.
2. Motor de regras cria plano inicial de treino + dieta + rotina semanal.
3. Usuário faz check-ins diários (simples e rápidos).
4. Motor analítico detecta padrões (falha recorrente, estagnação, fadiga).
5. Plano é reescrito automaticamente + gamificação reforça hábito.

## 2) Arquitetura técnica

### Stack escolhida
- **Front-end (sugerido para evolução):** React Native (Expo) + TypeScript.
- **Back-end (MVP implementado):** FastAPI + Python 3.11.
- **Persistência (MVP):** memória local em processo.
- **Persistência (produção):** PostgreSQL + Redis + fila assíncrona (Celery/RQ).

### Separação em motores
- `RuleEngine`: gera treino e dieta personalizados.
- `AnalysisEngine`: monitora progresso e detecta padrões.
- `GamificationEngine`: XP, níveis, streaks, conquistas e missões.
- `PlannerService`: orquestra os motores e replaneja semanalmente.

### Escalabilidade
- Serviços desacoplados por domínio lógico.
- Eventos de domínio (ex.: `DailyCheckinSubmitted`) para processamento assíncrono futuro.
- Estrutura preparada para memória de longo prazo por usuário (`history`, `compliance`, `adaptive_config`).

## 3) Modelagem de dados

Modelos principais no MVP:
- `UserProfile`: dados de onboarding + preferências + disponibilidade.
- `TrainingDayPlan`: foco, intensidade, volume e descanso por dia.
- `MealPlan`: calorias, macros e estratégia de simplicidade.
- `DailyTask` e `DailyPlan`: rotina diária de treino/refeições/hábitos.
- `ProgressSnapshot`: peso, energia, desempenho, aderência.
- `GamificationState`: XP, nível, streak, conquistas, missões.
- `AdaptiveRuleSet`: regras dinâmicas por usuário (ex.: `volume_multiplier`, `calorie_delta`).

## 4) Lógica dos algoritmos (implementada)

### Regra de treino (resumo)
```text
inputs: objetivo, nível, disponibilidade, preferência por treino curto
base_volume <- por nível
if objetivo = ganho_massa: intensidade +
if objetivo = emagrecimento: frequência +
if baixa aderência: volume -- e sessões mais curtas
variar estímulo por semana (força/hipertrofia/cardio/mobilidade)
```

### Regra de dieta (resumo)
```text
tdee <- fórmula simples por peso/atividade
if emagrecimento: calorias = tdee - 15%
if ganho_massa: calorias = tdee + 10%
macros por objetivo
se aderência baixa por 7 dias: simplificar plano alimentar
```

### Análise contínua
```text
if performance cai >= 5 dias seguidos: reduzir volume treino
if peso estagnado >= 14 dias e adesão alta: ajustar calorias
if energia baixa recorrente: inserir deload/recovery
```

### Gamificação
```text
XP diário por tarefas concluídas
streak semanal por consistência mínima
nível = floor(sqrt(xp/100)) + 1
missões adaptativas com base no padrão recente
```

## 5) MVP funcional

### Endpoints FastAPI
- `POST /onboarding` — cria perfil e regras iniciais.
- `GET /plan/{user_id}` — retorna plano atual.
- `POST /checkin/{user_id}` — registra check-in diário, atualiza análise e gamificação.
- `GET /weekly-report/{user_id}` — resumo semanal + explicação de ajustes.

### Rodar localmente
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 6) Estratégia de evolução

### Fase 1 (MVP atual)
- Onboarding inteligente.
- Plano dinâmico treino+dieta.
- Check-ins + ajuste automático.
- Gamificação base.

### Fase 2
- App React Native com notificações contextuais.
- Banco PostgreSQL e histórico completo.
- Recomendação de horário ótimo por usuário.
- Relatórios semanais visuais.

### Fase 3
- Modelo preditivo de risco de abandono.
- Missões hiperpersonalizadas.
- Integrações wearables (Apple Health, Google Fit).

## 7) Monetização B2C

### Freemium
- Onboarding + plano básico + streak/XP.

### Premium (assinatura)
- Ajuste avançado com ciclos periodizados.
- Relatórios profundos e insights preditivos.
- Biblioteca de receitas e substituições inteligentes.
- Co-pilot de recuperação (sono, estresse e deload).

---

## Observações de produto
- Não há templates fixos no motor: regras são compostas por perfil, aderência e progresso real.
- O sistema minimiza fricção e não depende de inputs constantes (check-ins curtos).
- A experiência usa linguagem motivadora e explicações simples.

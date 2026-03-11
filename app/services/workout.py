"""
Сервис для тренировочных программ
"""
from typing import Optional, List, Dict, Any
from ..utils import EXERCISE_LIBRARY, DAY_KEYS


def pick_exercise(group: str, offset: int = 0) -> Optional[Dict[str, str]]:
    """Выбор упражнения из библиотеки"""
    items = EXERCISE_LIBRARY.get(group, [])
    if not items:
        return None
    return items[offset % len(items)]


def bmi_category(height_cm: Optional[float], weight_kg: Optional[float]) -> str:
    """Определение категории BMI"""
    if not height_cm or not weight_kg:
        return "unknown"
    try:
        bmi = weight_kg / ((height_cm / 100) ** 2)
    except ZeroDivisionError:
        return "unknown"
    
    if bmi < 18.5:
        return "low"
    if bmi < 25:
        return "normal"
    if bmi < 30:
        return "high"
    return "obese"


def build_day_templates(day_count: int) -> Dict[int, List[List[str]]]:
    """Построение шаблонов тренировок для разного количества дней"""
    templates = {
        1: [["chest", "back", "legs", "shoulders", "abs"]],  # Full body
        2: [
            ["chest", "arms"],      # День 1: Грудь + трицепс
            ["back", "legs"]        # День 2: Спина + ноги
        ],
        3: [
            ["chest", "arms"],      # День 1: Грудь + руки (трицепс)
            ["back", "arms"],       # День 2: Спина + руки (бицепс)
            ["legs", "abs"]         # День 3: Ноги + пресс
        ],
        4: [
            ["chest", "abs"],       # День 1: Грудь + пресс
            ["back", "abs"],        # День 2: Спина + пресс
            ["legs"],               # День 3: Ноги
            ["shoulders", "arms"]   # День 4: Плечи + руки
        ],
        5: [
            ["chest", "arms"],      # День 1: Грудь + трицепс
            ["back", "abs"],        # День 2: Спина + пресс
            ["legs", "abs"],        # День 3: Ноги + пресс
            ["shoulders"],          # День 4: Плечи
            ["arms", "abs"]         # День 5: Руки + пресс
        ],
        6: [
            ["chest"],              # День 1: Грудь
            ["back"],               # День 2: Спина
            ["legs"],               # День 3: Ноги
            ["shoulders", "abs"],   # День 4: Плечи + пресс
            ["arms"],               # День 5: Руки
            ["abs"]                 # День 6: Пресс
        ],
        7: [
            ["chest", "abs"],       # День 1: Грудь + пресс
            ["back"],               # День 2: Спина
            ["legs"],               # День 3: Ноги
            ["shoulders"],          # День 4: Плечи
            ["arms", "abs"],        # День 5: Руки + пресс
            ["chest", "back"],      # День 6: Верх (грудь + спина)
            ["legs", "abs"]         # День 7: Низ (ноги + пресс)
        ],
    }
    return templates.get(day_count, templates[3])


def adjust_groups_for_goal(groups: List[str], goal: str) -> List[str]:
    """Корректирование группы мышц под цель"""
    goal = (goal or "").lower()
    adjusted = list(groups)
    
    # Для сжигания жира добавляем пресс
    if "жир" in goal:
        if "abs" not in adjusted:
            adjusted.append("abs")
    
    # Для рекомпозиции добавляем пресс для рельефа
    elif "рекомпозиция" in goal:
        if "abs" not in adjusted and len(adjusted) < 3:
            adjusted.append("abs")
    
    return adjusted


def generate_training_plan(
    available_days: List[int],
    goal: str,
    height_cm: Optional[float],
    weight_kg: Optional[float]
) -> Dict[str, List[Dict[str, str]]]:
    """Генерация программы тренировок"""
    day_count = max(1, min(len(available_days), 7))
    templates = build_day_templates(day_count)
    bmi_cat = bmi_category(height_cm, weight_kg)

    plan = {}
    for idx, day_index in enumerate(available_days[:len(templates)]):
        # Берем базовый шаблон для этого дня
        base_groups = templates[idx % len(templates)]
        
        # Корректируем под цель
        groups = adjust_groups_for_goal(base_groups, goal)
        
        # Если высокий BMI - добавляем пресс для любого дня
        if bmi_cat in ("high", "obese") and "abs" not in groups:
            groups.append("abs")
        
        # Подбираем упражнения для каждой группы
        day_exercises = []
        for g_idx, g in enumerate(groups):
            ex = pick_exercise(g, offset=idx + g_idx)
            if ex:
                day_exercises.append({"title": ex["title"], "gif": ex["gif"]})
        
        plan[DAY_KEYS[day_index]] = day_exercises
    
    return plan

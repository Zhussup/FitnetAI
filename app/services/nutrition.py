"""
Сервис для расчета питания
"""
from typing import Dict, Optional


def calculate_tdee(
    weight: float,
    height: float,
    age: int,
    gender: str,
    activity_level: float = 1.5
) -> float:
    """Расчет TDEE (Total Daily Energy Expenditure) по формуле Mifflin-St Jeor"""
    # Расчет BMR
    if gender and gender.upper() in ['М', 'M', 'MALE']:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # TDEE = BMR * Activity Multiplier
    tdee = bmr * activity_level
    return round(tdee, 0)


def calculate_nutrition_norms(
    weight: float,
    height: float,
    age: int,
    gender: str,
    program_name: str
) -> Dict[str, float]:
    """Расчет дневных норм питания на основе программы"""
    base_tdee = calculate_tdee(weight, height, age, gender)
    
    # Корректировка калорий в зависимости от программы
    if program_name == "Сжигание Жира":
        target_calories = base_tdee * 0.85  # 15% дефицит
        protein_per_kg = 2.2
        water_multiplier = 1.10
    elif program_name == "Набор Мышц":
        target_calories = base_tdee * 1.15  # 15% профицит
        protein_per_kg = 2.5
        water_multiplier = 1.05
    elif program_name == "Рекомпозиция Тела":
        target_calories = base_tdee * 1.0
        protein_per_kg = 2.0
        water_multiplier = 1.0
    else:  # Поддержание
        target_calories = base_tdee * 1.0
        protein_per_kg = 1.6
        water_multiplier = 1.0
    
    target_protein = weight * protein_per_kg
    base_water = weight * 35  # 35 ml per kg
    target_water = base_water * water_multiplier
    
    return {
        "target_calories": round(target_calories, 0),
        "target_protein": round(target_protein, 1),
        "target_water": round(target_water, 0),
        "base_tdee": round(base_tdee, 0)
    }

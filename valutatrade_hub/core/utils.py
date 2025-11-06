import json
import os
from typing import Any


def read_json(file_path: str) -> Any:
    """Чтение JSON файла"""
    if not os.path.exists(file_path):
        return [] if 'users' in file_path or 'portfolios' in file_path else {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(data: Any, file_path: str):
    """Запись в JSON файл"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def validate_currency_code(currency_code: str) -> str:
    """Валидация кода валюты"""
    if not currency_code or not isinstance(currency_code, str):
        raise ValueError("Код валюты должен быть непустой строкой")
    return currency_code.upper()


def validate_amount(amount: float) -> float:
    """Валидация суммы"""
    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError("Сумма должна быть положительным числом")
    return float(amount)
from datetime import date, timedelta

WINDOW_DAYS = 60
DECAY = 0.95  # за каждый день без выполнения сила падает на ~5%


def compute_habit_strength(logs: list, target_date: date | None = None) -> float:
    """
    Вычисляет «силу привычки» как взвешенную сумму выполнений за последние
    WINDOW_DAYS дней с экспоненциальным затуханием.

    Максимально возможный score при ежедневном выполнении = сумма геом. прогрессии:
        max_score = sum(DECAY^i for i in range(WINDOW_DAYS))
                  = (1 - DECAY^WINDOW_DAYS) / (1 - DECAY)

    Результат нормализуется в диапазон [0.0, 100.0].
    Один пропуск снижает силу примерно на 5% от текущего уровня, а не обнуляет.
    """
    if target_date is None:
        target_date = date.today()

    completed_dates = {log.date for log in logs if log.is_completed}

    raw_score = 0.0
    for age in range(WINDOW_DAYS):
        check_date = target_date - timedelta(days=age)
        if check_date in completed_dates:
            raw_score += DECAY ** age

    # Максимально возможный score (все 60 дней выполнены)
    max_score = (1.0 - DECAY ** WINDOW_DAYS) / (1.0 - DECAY)

    strength = (raw_score / max_score) * 100.0
    return round(min(max(strength, 0.0), 100.0), 2)

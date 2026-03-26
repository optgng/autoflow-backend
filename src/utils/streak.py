from datetime import date, timedelta

def compute_current_streak(logs: list) -> int:
    """Считает текущий непрерывный стрейк.
    Стрейк жив, если сегодня или вчера была отметка."""
    completed_dates = {log.date for log in logs if log.is_completed}
    if not completed_dates:
        return 0

    today = date.today()
    # Если сегодня не отмечено — проверяем с вчера (стрейк ещё "живой")
    check = today if today in completed_dates else today - timedelta(days=1)

    streak = 0
    while check in completed_dates:
        streak += 1
        check -= timedelta(days=1)

    return streak
def format_hours(hours):
    """Преобразует количество часов в читаемый формат."""
    if hours is None:
        return "N/A"
    hours = float(hours)
    if hours < 1:
        return f"{int(hours * 60)} min"
    elif hours < 24:
        return f"{hours:.1f} h"
    else:
        days = hours / 24
        return f"{days:.1f} days"

def resolution_time_hours(created_at, resolved_at):
    if resolved_at is None:
        return None
    delta = resolved_at - created_at
    return delta.total_seconds() / 3600.0

def sla_status(resolution_hours, sla_hours):
    if resolution_hours is None:
        return "In Progress"
    if resolution_hours <= sla_hours:
        return "Met"
    return "Breached"
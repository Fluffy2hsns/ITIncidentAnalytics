import pandas as pd

def style_status(status):
    """Возвращает CSS-класс или цвет для статуса."""
    colors = {
        'New': 'blue',
        'Assigned': 'orange',
        'In Progress': 'purple',
        'Resolved': 'green',
        'Closed': 'gray'
    }
    return colors.get(status, 'black')

def style_priority(priority):
    colors = {
        'Low': 'green',
        'Medium': 'blue',
        'High': 'orange',
        'Critical': 'red'
    }
    return colors.get(priority, 'black')
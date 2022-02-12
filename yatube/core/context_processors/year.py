import datetime as d


def year(request):
    """Добавляет переменную с текущим годом."""
    current_year = d.datetime.now()
    current_year_string = current_year.strftime('%Y')
    current_year_int = int(current_year_string)
    return {
        'year': current_year_int,
    }

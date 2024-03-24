import datetime


def year(request):
    """Добавляет в контекст переменную о дате в данный момент"""
    return {"year": datetime.datetime.today().year}

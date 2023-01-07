from django.utils import timezone


def year(request):
    """Добавляет переменную с текущим годом."""
    yearnow = timezone.now().strftime("%Y")
    return {
        'year': yearnow
    }

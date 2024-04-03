from django.utils import timezone

def get_graduation_years():
    current_year = timezone.now().year
    return [(year, str(year)) for year in range(current_year, current_year + 8)]
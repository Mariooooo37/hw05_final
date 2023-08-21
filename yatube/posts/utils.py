from django.core.paginator import Paginator
from django.db import connection, reset_queries


POST_IN_PAGE = 10


def paginator(queryset, request):
    paginator = Paginator(queryset, POST_IN_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def print_all_queries_decorator(func):
    def wrapper(*args, **kwargs):
        reset_queries()
        results = func(*args, **kwargs)
        for query_info in connection.queries:
            print()
            print('SQL:', query_info['sql'])
            print('TIME:', query_info['time'])
            print()
            return results
    return wrapper

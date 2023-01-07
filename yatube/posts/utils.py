from django.core.paginator import Paginator

POST_IN_PAGE = 10


def paginator(queryset, request):
    paginator = Paginator(queryset, POST_IN_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj

from django.core.paginator import Paginator


def paginator_calculate(request, posts, quantity_of_posts_on_page):
    paginator = Paginator(posts, quantity_of_posts_on_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

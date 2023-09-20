from rest_framework.pagination import PageNumberPagination


class ImagePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    max_page_size = 25

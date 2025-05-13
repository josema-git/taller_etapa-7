from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class Pagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'start_page': (self.page.number-1) * self.page_size,
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class PostPagination(Pagination):
    page_size = 10

class CommentPagination(Pagination):
    page_size = 10

class LikePagination(Pagination):
    page_size = 15
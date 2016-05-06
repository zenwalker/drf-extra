from rest_framework.response import Response
from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
)


class HeaderPaginationMixin:
    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()

        if next_url is not None and previous_url is not None:
            link = '<{next_url}>; rel="next", <{previous_url}>; rel="prev"'
        elif next_url is not None:
            link = '<{next_url}>; rel="next"'
        elif previous_url is not None:
            link = '<{previous_url}>; rel="prev"'
        else:
            link = ''

        link = link.format(next_url=next_url, previous_url=previous_url)
        headers = {'Items-Count': self.get_items_count()}
        if link:
            headers['Pagination'] = link
        return Response(data, headers=headers)

    def get_items_count(self):
        raise NotImplementedError()


class PageHeaderPagination(HeaderPaginationMixin, PageNumberPagination):
    page_size = 30

    def get_items_count(self):
        return self.count.paginator.count


class OffsetHeaderPagination(HeaderPaginationMixin, LimitOffsetPagination):
    page_size = 30

    def get_items_count(self):
        return self.count

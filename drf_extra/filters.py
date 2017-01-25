from rest_framework.filters import BaseFilterBackend
from django.core.exceptions import FieldError
from django.db.models import Q
from functools import reduce
import operator
import json

from .exceptions import FilterException

operators = {
    'or': operator.or_,
    'and': operator.and_,
}


class QuerySetFilterBackend(BaseFilterBackend):
    default_condition = 'and'
    filter_param_name = 'filter'
    condition_param_name = 'cond'

    def filter_queryset(self, request, queryset, view):
        condition = operators[request.GET.get(self.condition_param_name, self.default_condition)]
        required_fields = getattr(view, 'required_filter_fields', [])
        filter_aliases = getattr(view, 'filter_aliases', {})
        queries = request.GET.getlist(self.filter_param_name)
        distinct_field = request.GET.get('distinct')

        # decode from json and apply aliases for query keys
        queries = [{filter_aliases.get(key, key): value
                    for key, value in json.loads(query).items()}
                    for query in queries]  # noqa

        if required_fields:
            query_keys = set(sum([list(q.keys()) for q in queries], []))
            if len(query_keys.intersection(required_fields)) != len(required_fields):
                raise FilterException('Filter field(s) {} is required.'.format(', '.join(required_fields)))

        if queries:
            try:
                filter_args = reduce(condition, [Q(**q) for q in queries])
                queryset = queryset.filter(filter_args)
                if distinct_field:
                    return queryset.distinct(distinct_field)
            except (ValueError, FieldError, TypeError) as e:
                raise FilterException(e)

        return queryset

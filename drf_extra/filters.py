from rest_framework.filters import BaseFilterBackend
from django.db.models import Q
from functools import reduce
import operator
import json

operators = {
    'or': operator.or_,
    'and': operator.and_,
}


class QueryFilterBackend(BaseFilterBackend):
    condition_param_name = 'cond'
    default_condition = 'and'
    filter_param_name = 'q'

    def filter_queryset(self, request, queryset, view):
        condition = operators[request.GET.get(self.condition_param_name, self.default_condition)]
        queries = request.get.getlist(self.filter_param_name)
        distinct_field = request.GET.get('distinct')

        if queries:
            try:
                filter_args = reduce(condition, [Q(**json.loads(q)) for q in queries])
                queryset = queryset.filter(filter_args)
                if distinct_field:
                    return queryset.distinct(distinct_field)
            except json.JSONDecodeError:
                pass

        return queryset

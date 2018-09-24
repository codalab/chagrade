from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_extensions.cache.decorators import cache_response

from api.caching import QueryParamsKeyConstructor
from utils.search import get_search_client, get_results, get_default_search_results


class SearchView(APIView):

    @cache_response(key_func=QueryParamsKeyConstructor(), timeout=60)
    def get(self, request, version="v1"):
        # Get search data
        query = request.GET.get('q', '')
        sorting = request.GET.get('sorting')
        date_flags = request.GET.get('date_flags')
        start = request.GET.get('start_date')
        end = request.GET.get('end_date')
        producer = request.GET.get('producer')

        # Setup ES connection, excluding HTML text from our results
        s = get_search_client()
        data = {
            "results": [],
            "showing_default_results": False,
        }

        # Do search/filtering/sorting
        s = self._search(s, query)
        s = self._filter(s, date_flags, start, end, producer)
        s = self._sort(s, sorting, query)

        # Get results and prepare them
        data["results"] = get_results(s)

        if not data["results"]:
            data["showing_default_results"] = True
            data["results"] = get_default_search_results()

        return Response(data)

    def _search(self, search, query):
        if query and query != ' ':
            search = search.query(
                "multi_match",
                query=query,
                type="best_fields",
                fuzziness='auto',
                fields=["title^5", "description^3", "html_text^2", "created_by"]
            )
            # s = s.highlight('title', fragment_size=50)
            # s = s.suggest('suggestions', query, term={'field': 'title'})
        return search

    def _filter(self, search, date_flags, start, end, producer):
        # This month/this year
        if date_flags == "this_month":
            search = search.filter('range', start={
                'gte': "now/M",
                'lte': "now/M",
            })
        if date_flags == "this_year":
            search = search.filter('range', start={
                'gte': "now/y",
                'lte': "now/y",
            })

        # Start/end range
        date_args = {}
        if start:
            date_args['gte'] = start
        if end:
            date_args['lte'] = end
        if date_args:
            date_args['format'] = 'date_optional_time'
            search = search.filter('range', start=date_args)

        # Active competitions, ones with submissions in the last 30 days
        if date_flags and date_flags == "active":
            search = search.filter('term', is_active=True)
        if producer:
            search = search.filter('term', producer__id=producer)
        return search

    def _sort(self, search, sorting, query):
        # Make a positional list with `_score`(relevancy ranking of keyword search) as the first entry if we
        # have a valid query. Then tack on whatever field we sort by
        sort_params = ['_score'] if query else []
        if sorting == 'participant_count':
            sort_params.append('-participant_count')
        elif sorting == 'prize':
            sort_params.append('-prize')
        elif sorting == 'deadline':
            sort_params.append('current_phase_deadline')
        return search.sort(*sort_params)

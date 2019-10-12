import requests
from rest_framework import views
from rest_framework.response import Response


class GitAggregator(views.APIView):
    """The class that shows aggregation of several Git hostings data."""
    def get(self, request):
        profiles = request.GET.getlist('url')  # no need to check for exceptions
        try:
            data = {}  # aggregate_data(profiles)
        except requests.exceptions.RequestException as e:
            # As the API complicates, should to create a special class for error responses.
            # I did this in the main Turing challenge.
            return Response({'error': 'ERR1', 'message': str(e)})
        else:
            return Response({'error': 'OK', 'data': data})

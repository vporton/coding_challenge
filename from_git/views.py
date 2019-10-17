import requests
from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response

from from_git.aggregator import aggregate_data, WrongURLException


class GitAggregator(views.APIView):
    """Show aggregation of several Git hostings data."""
    def get(self, request):
        profiles = request.GET.getlist('url')  # no need to check for exceptions
        try:
            data, missing = aggregate_data(profiles)
        except requests.exceptions.RequestException as e:
            # As the API complicates, should to create a special class for error responses.
            # I did this in the main Turing challenge.
            return Response({'error': 'ERR2', 'message': str(e)}, status=500)
        except WrongURLException as e:
            return Response({'error': 'ERR3', 'message': str(e)}, status=400)
        except Exception as e:
            return Response({'error': 'ERRX', 'message': str(e)}, status=500)
        else:
            return Response({'error': 'OK', 'data': data, 'missing': missing})


class GitAggregatorTest(views.View):
    def get(self, request):
        return render(request, 'tests/git-aggregator-test.html')
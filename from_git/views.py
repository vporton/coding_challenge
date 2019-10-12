from rest_framework import views
from rest_framework.response import Response


class GitAggregator(views.APIView):
    """The class that shows aggregation of several Git hostings data."""
    def get(self, request):
        return Response({})

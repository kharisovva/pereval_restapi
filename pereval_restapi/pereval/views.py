from django.db import DatabaseError
from rest_framework import status as http_status
from rest_framework.response import Response
from rest_framework.views import APIView

from pereval.data_manager import PerevalDataManager
from pereval.serializers import SubmitDataSerializer


class SubmitDataView(APIView):
    def post(self, request):
        serializer = SubmitDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": 400, "message": serializer.errors, "id": None}, status=http_status.HTTP_400_BAD_REQUEST
            )

        try:
            manager = PerevalDataManager()
            pereval = manager.submit_data(serializer.validated_data)
            return Response({"status": 200, "message": None, "id": pereval.id}, status=http_status.HTTP_200_OK)
        except DatabaseError:
            return Response(
                {"status": 500, "message": "Ошибка подключения к базе данных", "id": None},
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except ValueError as e:
            return Response({"status": 400, "message": str(e), "id": None}, status=http_status.HTTP_400_BAD_REQUEST)

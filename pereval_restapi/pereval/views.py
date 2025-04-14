import json

from django.db import DatabaseError
from rest_framework import status as http_status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from pereval.data_manager import PerevalDataManager
from pereval.serializers import SubmitDataSerializer


class SubmitDataView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            data = json.loads(request.data.get("data", "{}"))
            serializer = SubmitDataSerializer(data=data)
            if not serializer.is_valid():
                return Response(
                    {"status": 400, "message": serializer.errors, "id": None}, status=http_status.HTTP_400_BAD_REQUEST
                )

            image_files = request.FILES.getlist("images", [])
            images_data = serializer.validated_data.get("pereval", {}).get("images", [])

            if images_data and len(image_files) != len(images_data):
                return Response(
                    {
                        "status": 400,
                        "message": "Количество загруженных файлов не совпадает с количеством заголовков",
                        "id": None,
                    },
                    status=http_status.HTTP_400_BAD_REQUEST,
                )

            manager = PerevalDataManager()
            pereval = manager.submit_data(serializer.validated_data, image_files)
            return Response({"status": 200, "message": None, "id": pereval.id}, status=http_status.HTTP_200_OK)

        except json.JSONDecodeError:
            return Response(
                {"status": 400, "message": "Некорректный формат JSON в поле data", "id": None},
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        except DatabaseError:
            return Response(
                {"status": 500, "message": "Ошибка подключения к базе данных", "id": None},
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except ValueError as e:
            return Response({"status": 400, "message": str(e), "id": None}, status=http_status.HTTP_400_BAD_REQUEST)

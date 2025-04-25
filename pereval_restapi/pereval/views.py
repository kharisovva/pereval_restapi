import json

from django.db import DatabaseError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status as http_status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from pereval.data_manager import PerevalDataManager
from pereval.models import Pereval
from pereval.serializers import PerevalDetailSerializer, SubmitDataSerializer


class SubmitDataView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="Получить список перевалов по email пользователя или данные перевала по ID.",
        manual_parameters=[
            openapi.Parameter(
                "user__email",
                openapi.IN_QUERY,
                description="Email пользователя для фильтрации перевалов",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Список перевалов или данные перевала", schema=PerevalDetailSerializer(many=True)
            ),
            400: openapi.Response(
                description="Ошибка: Email обязателен",
                examples={"application/json": {"status": 400, "message": "Email обязателен"}},
            ),
            404: openapi.Response(
                description="Перевал не найден",
                examples={"application/json": {"status": 404, "message": "Перевал не найден"}},
            ),
            500: openapi.Response(
                description="Ошибка сервера",
                examples={"application/json": {"status": 500, "message": "Ошибка сервера"}},
            ),
        },
    )
    def get(self, request, id=None):
        # Обработка GET /submitData/<id>/
        if id is not None:
            try:
                pereval = Pereval.objects.get(id=id)
                serializer = PerevalDetailSerializer(pereval, context={"request": request})
                return Response(serializer.data, status=http_status.HTTP_200_OK)

            except Pereval.DoesNotExist:
                return Response(
                    {"status": 404, "message": "Перевал не найден", "id": None}, status=http_status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {"status": 500, "message": f"Ошибка сервера: {str(e)}", "id": None},
                    status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Обработка GET /submitData/?user__email=<email>
        email = request.query_params.get("user__email")
        if not email:
            return Response({"status": 400, "message": "Email обязателен"}, status=http_status.HTTP_400_BAD_REQUEST)

        try:
            perevals = Pereval.objects.filter(user__email=email)
            serializer = PerevalDetailSerializer(perevals, many=True, context={"request": request})
            return Response(serializer.data, status=http_status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"status": 500, "message": f"Ошибка сервера: {str(e)}"},
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Создать новый перевал с данными пользователя, района, координат, уровней сложности и изображений.",
        manual_parameters=[
            openapi.Parameter(
                "data",
                openapi.IN_FORM,
                description="JSON-строка с данными перевала (user, area, pereval)",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "images",
                openapi.IN_FORM,
                description="Файлы изображений (multipart/form-data)",
                type=openapi.TYPE_FILE,
                required=True,
            ),
        ],
        consumes=["multipart/form-data"],
        responses={
            200: openapi.Response(
                description="Перевал успешно создан",
                examples={"application/json": {"status": 200, "message": "", "id": 1}},
            ),
            400: openapi.Response(
                description="Ошибка валидации или формата данных",
                examples={
                    "application/json": {"status": 400, "message": "Некорректный формат JSON в поле data", "id": None}
                },
            ),
            500: openapi.Response(
                description="Ошибка сервера",
                examples={
                    "application/json": {"status": 500, "message": "Ошибка подключения к базе данных", "id": None}
                },
            ),
        },
    )
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
            return Response({"status": 200, "message": "", "id": pereval.id}, status=http_status.HTTP_200_OK)

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

    @swagger_auto_schema(
        operation_description="Обновить существующий перевал (доступно только для статуса 'new').",
        manual_parameters=[
            openapi.Parameter(
                "data",
                openapi.IN_FORM,
                description="JSON-строка с данными перевала (area, pereval)",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "images",
                openapi.IN_FORM,
                description="Файлы изображений (multipart/form-data)",
                type=openapi.TYPE_FILE,
                required=True,
            ),
        ],
        consumes=["multipart/form-data"],
        responses={
            200: openapi.Response(
                description="Перевал успешно обновлен", examples={"application/json": {"state": 1, "message": ""}}
            ),
            400: openapi.Response(
                description="Ошибка валидации, статуса или формата данных",
                examples={
                    "application/json": {"state": 0, "message": "Редактирование возможно только для статуса 'new'"}
                },
            ),
            404: openapi.Response(
                description="Перевал не найден",
                examples={"application/json": {"state": 0, "message": "Перевал не найден"}},
            ),
            500: openapi.Response(
                description="Ошибка сервера",
                examples={"application/json": {"state": 0, "message": "Неизвестная ошибка"}},
            ),
        },
    )
    def patch(self, request, id=None):
        try:
            data = json.loads(request.data.get("data", "{}"))
            serializer = SubmitDataSerializer(data=data)
            if not serializer.is_valid():
                return Response({"state": 0, "message": serializer.errors}, status=http_status.HTTP_400_BAD_REQUEST)

            image_files = request.FILES.getlist("images", [])
            images_data = serializer.validated_data.get("pereval", {}).get("images", [])

            if images_data and not image_files:
                return Response(
                    {"state": 0, "message": "Файлы изображений не переданы"}, status=http_status.HTTP_400_BAD_REQUEST
                )

            if images_data and len(image_files) != len(images_data):
                return Response(
                    {"state": 0, "message": "Количество загруженных файлов не совпадает с количеством заголовков"},
                    status=http_status.HTTP_400_BAD_REQUEST,
                )

            Pereval.objects.get(id=id)

            manager = PerevalDataManager()
            area = manager.create_area(serializer.validated_data["area"])

            manager.update_pereval(
                pereval_id=id, pereval_data=serializer.validated_data["pereval"], area=area, image_files=image_files
            )
            return Response({"state": 1, "message": ""}, status=http_status.HTTP_200_OK)

        except Pereval.DoesNotExist:
            return Response({"state": 0, "message": "Перевал не найден"}, status=http_status.HTTP_404_NOT_FOUND)
        except json.JSONDecodeError:
            return Response(
                {"state": 0, "message": "Некорректный формат JSON в поле data"}, status=http_status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response({"state": 0, "message": str(e)}, status=http_status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"state": 0, "message": f"Неизвестная ошибка: {str(e)}"},
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

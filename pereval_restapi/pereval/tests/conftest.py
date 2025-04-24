import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from pereval.data_manager import PerevalDataManager
from pereval.models import Area, Image, Level, Pereval, User


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def test_user(db):
    user = User.objects.create(
        email="testuser@email.tld", first_name="Тест", last_name="Тестов", patronymic="Тестович", phone="79999999999"
    )
    return user


@pytest.fixture
def test_area(db):
    area = Area.objects.create(title="Тестовый хребет")
    return area


@pytest.fixture
def test_pereval(db, test_user, test_area):
    pereval = Pereval.objects.create(
        beauty_title="пер.",
        title="Тестовый перевал",
        other_titles="Тест",
        connect="",
        user=test_user,
        area=test_area,
        latitude=45.0,
        longitude=7.0,
        height=1000,
        status="new",
    )
    Level.objects.create(pereval=pereval, winter="", summer="1А", autumn="1А", spring="")
    return pereval


@pytest.fixture
def test_image(db, test_pereval):
    image_file = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
    image = Image.objects.create(pereval=test_pereval, title="Тестовое изображение", image=image_file)
    return image


@pytest.fixture
def test_data():
    return {
        "user": {
            "email": "testuser@email.tld",
            "first_name": "Тест",
            "last_name": "Тестов",
            "patronymic": "Тестович",
            "phone": "79999999999",
        },
        "area": {"title": "Тестовый хребет", "parent_id": None},
        "pereval": {
            "beauty_title": "пер.",
            "title": "Тестовый перевал",
            "other_titles": "Тест",
            "connect": "",
            "coords": {"latitude": 45.0, "longitude": 7.0, "height": 1000},
            "level": {"winter": "", "summer": "1А", "autumn": "1А", "spring": ""},
            "images": [{"title": "Тестовое изображение"}],
        },
    }


@pytest.fixture
def test_image_file():
    return SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")


@pytest.fixture
def data_manager():
    return PerevalDataManager()

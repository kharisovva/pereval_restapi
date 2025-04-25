import json

import pytest
from django.urls import reverse

from pereval.models import Image, Pereval


class TestSubmitDataAPI:
    @pytest.fixture(autouse=True)
    def setup(self, client, test_data):
        self.client = client
        self.test_data = test_data

    @pytest.mark.django_db
    def test_post_submit_data(self, test_image_file):
        url = reverse("submit_data")
        data = {"data": json.dumps(self.test_data), "images": test_image_file}
        response = self.client.post(url, data, format="multipart")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == 200
        assert response_data["message"] == ""
        assert "id" in response_data
        assert Pereval.objects.count() == 1
        assert Image.objects.count() == 1
        pereval = Pereval.objects.first()
        assert response_data["id"] == pereval.id
        assert pereval.title == "Тестовый перевал"
        assert pereval.user.email == "testuser@email.tld"

    def test_get_submit_data_by_id(self, test_pereval, test_image):
        url = reverse("submit_data_detail", args=[test_pereval.id])
        response = self.client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_pereval.id
        assert data["title"] == "Тестовый перевал"
        assert data["status"] == "new"
        assert len(data["images"]) == 1
        assert data["images"][0]["title"] == "Тестовое изображение"

    def test_patch_submit_data(self, test_pereval, test_image_file):
        url = reverse("submit_data_detail", args=[test_pereval.id])
        updated_data = self.test_data.copy()
        updated_data["pereval"].update(
            {
                "title": "Обновленный перевал",
                "coords": {"latitude": 46.0, "longitude": 8.0, "height": 1500},
                "level": {"winter": "1Б", "summer": "1Б", "autumn": "1Б", "spring": ""},
                "images": [{"title": "Новое изображение"}],
            }
        )
        data = {"data": json.dumps(updated_data), "images": test_image_file}
        response = self.client.patch(url, data, format="multipart")
        assert response.status_code == 200
        assert response.json() == {"state": 1, "message": ""}
        pereval = Pereval.objects.get(id=test_pereval.id)
        assert pereval.title == "Обновленный перевал"
        assert pereval.latitude == 46.0
        assert pereval.level.winter == "1Б"
        assert pereval.images.count() == 1
        assert pereval.images.first().title == "Новое изображение"

    def test_patch_submit_data_not_new(self, test_pereval, test_image_file):
        test_pereval.status = "pending"
        test_pereval.save()
        url = reverse("submit_data_detail", args=[test_pereval.id])
        data = {"data": json.dumps(self.test_data), "images": test_image_file}
        response = self.client.patch(url, data, format="multipart")
        assert response.status_code == 400
        assert response.json()["state"] == 0
        assert "Редактирование возможно только для статуса 'new'" in response.json()["message"]

    def test_get_submit_data_by_email(self, test_pereval, test_image):
        url = reverse("submit_data") + "?user__email=testuser@email.tld"
        response = self.client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == test_pereval.id
        assert data[0]["title"] == "Тестовый перевал"
        assert data[0]["user"]["email"] == "testuser@email.tld"

    def test_get_submit_data_no_email(self):
        url = reverse("submit_data")
        response = self.client.get(url)
        assert response.status_code == 400
        assert response.json() == {"status": 400, "message": "Email обязателен"}

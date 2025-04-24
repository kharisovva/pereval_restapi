import pytest

from pereval.models import Area, Image, Level, Pereval, User


class TestPerevalDataManager:
    @pytest.fixture(autouse=True)
    def _setup(self, data_manager, test_data):
        self.data_manager = data_manager
        self.test_data = test_data

    @pytest.mark.django_db
    def test_create_user_new(self):
        user_data = self.test_data["user"]
        user = self.data_manager.create_user(user_data)
        assert isinstance(user, User)
        assert user.email == "testuser@email.tld"
        assert user.first_name == "Тест"
        assert user.last_name == "Тестов"
        assert User.objects.count() == 1

    def test_create_user_existing(self, test_user):
        user_data = {
            "email": "testuser@email.tld",
            "first_name": "Другое",
            "last_name": "Имя",
            "patronymic": "Другое",
            "phone": "78888888888",
        }
        user = self.data_manager.create_user(user_data)
        assert user == test_user
        assert user.first_name == "Тест"  # Не изменилось
        assert User.objects.count() == 1

    @pytest.mark.django_db
    def test_create_area_new(self):
        area_data = self.test_data["area"]
        area = self.data_manager.create_area(area_data)
        assert isinstance(area, Area)
        assert area.title == "Тестовый хребет"
        assert area.parent is None
        assert Area.objects.count() == 1

    def test_create_area_existing(self, test_area):
        area_data = {"title": "Тестовый хребет", "parent_id": None}
        area = self.data_manager.create_area(area_data)
        assert area == test_area
        assert Area.objects.count() == 1

    def test_create_pereval(self, test_user, test_area):
        pereval_data = self.test_data["pereval"]
        pereval = self.data_manager.create_pereval(pereval_data, test_user, test_area)
        assert isinstance(pereval, Pereval)
        assert pereval.title == "Тестовый перевал"
        assert pereval.latitude == 45.0
        assert pereval.status == "new"
        assert Pereval.objects.count() == 1

    def test_update_pereval_success(self, test_pereval, test_area, test_image_file):
        updated_data = self.test_data["pereval"].copy()
        updated_data.update(
            {
                "title": "Обновленный перевал",
                "coords": {"latitude": 46.0, "longitude": 8.0, "height": 1500},
                "level": {"winter": "1Б", "summer": "1Б", "autumn": "1Б", "spring": ""},
                "images": [{"title": "Новое изображение"}],
            }
        )
        pereval = self.data_manager.update_pereval(test_pereval.id, updated_data, test_area, [test_image_file])
        assert pereval.title == "Обновленный перевал"
        assert pereval.latitude == 46.0
        assert pereval.level.winter == "1Б"
        assert pereval.images.count() == 1
        assert pereval.images.first().title == "Новое изображение"

    def test_update_pereval_not_new(self, test_pereval, test_area):
        test_pereval.status = "pending"
        test_pereval.save()
        with pytest.raises(ValueError, match="Редактирование возможно только для статуса 'new'"):
            self.data_manager.update_pereval(test_pereval.id, self.test_data["pereval"], test_area)

    def test_create_level(self, test_pereval):
        level_data = {"winter": "1А", "summer": "1Б", "autumn": "1А", "spring": ""}
        Level.objects.filter(pereval=test_pereval).delete()
        level = self.data_manager.create_level(test_pereval, level_data)
        assert isinstance(level, Level)
        assert level.winter == "1А"
        assert level.summer == "1Б"
        assert Level.objects.count() == 1

    def test_create_images(self, test_pereval, test_image_file):
        images_data = [{"title": "Тестовое изображение"}]
        images = self.data_manager.create_images(test_pereval, images_data, [test_image_file])
        assert len(images) == 1
        assert images[0].title == "Тестовое изображение"
        assert Image.objects.count() == 1

    @pytest.mark.django_db
    def test_submit_data(self, test_image_file):
        pereval = self.data_manager.submit_data(self.test_data, [test_image_file])
        assert isinstance(pereval, Pereval)
        assert pereval.title == "Тестовый перевал"
        assert pereval.user.email == "testuser@email.tld"
        assert pereval.area.title == "Тестовый хребет"
        assert pereval.images.count() == 1
        assert Pereval.objects.count() == 1
        assert Level.objects.count() == 1
        assert Image.objects.count() == 1

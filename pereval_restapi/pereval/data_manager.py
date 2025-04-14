from django.db import IntegrityError

from pereval.models import Area, Image, Level, Pereval, User


class PerevalDataManager:
    """Класс для работы с данными о перевалах и связанных сущностях."""

    def create_user(self, user_data):
        """
        Создает или возвращает существующего пользователя.
        :param user_data: dict с полями email, first_name, last_name, patronymic, phone
        :return: объект User
        """
        email = user_data.get("email")
        if not email:
            raise ValueError("Email обязателен")
        user = User.objects.filter(email=email).first()
        if user:
            return user

        else:
            user = User.objects.create(
                email=email,
                first_name=user_data.get("first_name", ""),
                last_name=user_data.get("last_name", ""),
                patronymic=user_data.get("patronymic"),
                phone=user_data.get("phone"),
            )
            return user

    def create_area(self, area_data):
        """
        Создает или возвращает существующий район.
        :param area_data: dict с полями title, parent_id (опционально)
        :return: объект Area
        """
        title = area_data.get("title")
        parent_id = area_data.get("parent_id")

        try:
            if parent_id:
                parent = Area.objects.get(id=parent_id)
            else:
                parent = None

            area, created = Area.objects.get_or_create(title=title, defaults={"parent": parent})
            return area
        except Area.DoesNotExist:
            raise ValueError(f"Район с parent_id {parent_id} не найден")
        except IntegrityError:
            raise ValueError(f"Ошибка при создании района {title}")

    def create_pereval(self, pereval_data, user, area):
        """
        Создает новый перевал.
        :param pereval_data: dict с полями beauty_title, title, other_titles, connect,
                            coords (latitude, longitude, height), level (winter, summer, autumn, spring),
                            images (список {title, image_path})
        :param user: объект User
        :param area: объект Area
        :return: объект Pereval
        """
        try:
            pereval = Pereval.objects.create(
                beauty_title=pereval_data.get("beauty_title"),
                title=pereval_data["title"],
                other_titles=pereval_data.get("other_titles"),
                connect=pereval_data.get("connect"),
                user=user,
                area=area,
                latitude=pereval_data["coords"]["latitude"],
                longitude=pereval_data["coords"]["longitude"],
                height=pereval_data["coords"]["height"],
                status="new",
            )
            return pereval
        except IntegrityError:
            raise ValueError("Перевал с такими данными уже существует")

    def create_level(self, pereval, level_data):
        """
        Создает уровни сложности для перевала.
        :param pereval: объект Pereval
        :param level_data: dict с полями winter, summer, autumn, spring
        :return: объект Level
        """
        try:
            level = Level.objects.create(
                pereval=pereval,
                winter=level_data.get("winter"),
                summer=level_data.get("summer"),
                autumn=level_data.get("autumn"),
                spring=level_data.get("spring"),
            )
            return level
        except IntegrityError:
            raise ValueError(f"Уровень сложности для перевала {pereval.id} уже существует")

    def create_images(self, pereval, images_data, image_files):
        """
        Создает изображения для перевала.
        :param pereval: объект Pereval
        :param images_data: список dict с полем title
        :param image_files: список файлов
        :return: список объектов Image
        """
        if len(images_data) != len(image_files):
            raise ValueError("Количество заголовков изображений не совпадает с количеством файлов")

        images = []
        for image_data, image_file in zip(images_data, image_files):
            try:
                image = Image.objects.create(pereval=pereval, title=image_data.get("title"), image=image_file)
                images.append(image)
            except Exception as e:
                raise ValueError(f"Ошибка при создании изображения: {str(e)}")
        return images

    def submit_data(self, data, image_files=None):
        """
        Основной метод для добавления полного набора данных о перевале.
        :param data: dict с полями user, area, pereval
        :param images_data: список dict с полями title, image (файл)
        :return: объект Pereval
        """
        user = self.create_user(data["user"])
        area = self.create_area(data["area"])
        pereval = self.create_pereval(data["pereval"], user, area)
        self.create_level(pereval, data["pereval"]["level"])

        if image_files and data.get("pereval", {}).get("images"):
            self.create_images(pereval, data["pereval"]["images"], image_files)

        return pereval

from django.db import models


class User(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.patronymic or ''}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Area(models.Model):
    title = models.CharField(max_length=255)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Район"
        verbose_name_plural = "Районы"


class Pereval(models.Model):
    STATUS_CHOICES = [
        ("new", "Новый"),
        ("pending", "На модерации"),
        ("accepted", "Принят"),
        ("rejected", "Отклонён"),
    ]

    beauty_title = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=255)
    other_titles = models.CharField(max_length=255, blank=True, null=True)
    connect = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    height = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")

    def __str__(self):
        return f"{self.beauty_title or ''} {self.title}"

    class Meta:
        verbose_name = "Перевал"
        verbose_name_plural = "Перевалы"
        constraints = [models.UniqueConstraint(fields=["title", "latitude", "longitude"], name="unique_pereval")]


class Level(models.Model):
    pereval = models.OneToOneField(Pereval, on_delete=models.CASCADE)
    winter = models.CharField(max_length=10, blank=True, null=True)
    summer = models.CharField(max_length=10, blank=True, null=True)
    autumn = models.CharField(max_length=10, blank=True, null=True)
    spring = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"Уровни для {self.pereval}"

    class Meta:
        verbose_name = "Уровень сложности"
        verbose_name_plural = "Уровни сложности"


class Image(models.Model):
    pereval = models.ForeignKey(Pereval, on_delete=models.CASCADE, related_name="images")
    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to="images/%Y/%m/%d/")
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Изображение {self.id}"

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"


class ActivityType(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тип активности"
        verbose_name_plural = "Типы активности"

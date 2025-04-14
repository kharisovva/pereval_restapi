from rest_framework import serializers
from .models import User, Area, Pereval, Level, Image


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'patronymic', 'phone']

    def validate(self, data):
        if not data.get('email') or not data.get('first_name') or not data.get('last_name'):
            raise serializers.ValidationError("Поля email, first_name, last_name обязательны")
        return data


class AreaSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Area
        fields = ['title', 'parent_id']

    def validate(self, data):
        if not data.get('title'):
            raise serializers.ValidationError("Поле title обязательно")
        return data


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['winter', 'summer', 'autumn', 'spring']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['title', 'image_path']

    def validate(self, data):
        if not data.get('image_path'):
            raise serializers.ValidationError("Поле image_path обязательно")
        return data


class CoordsSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    height = serializers.IntegerField()

    def validate(self, data):
        if not (-90 <= data['latitude'] <= 90):
            raise serializers.ValidationError("Широта должна быть в диапазоне от -90 до 90")
        if not (-180 <= data['longitude'] <= 180):
            raise serializers.ValidationError("Долгота должна быть в диапазоне от -180 до 180")
        if data['height'] < 0:
            raise serializers.ValidationError("Высота не может быть отрицательной")
        return data


class PerevalSerializer(serializers.Serializer):
    beauty_title = serializers.CharField(max_length=50, required=False, allow_null=True)
    title = serializers.CharField(max_length=255)
    other_titles = serializers.CharField(max_length=255, required=False, allow_null=True)
    connect = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    coords = CoordsSerializer()
    level = LevelSerializer()
    images = ImageSerializer(many=True, required=False)

    def validate(self, data):
        if not data['title'].strip():
            raise serializers.ValidationError("Название перевала не может быть пустым")
        return data


class SubmitDataSerializer(serializers.Serializer):
    user = UserSerializer()
    area = AreaSerializer()
    pereval = PerevalSerializer()
    images = ImageSerializer(many=True, required=False)
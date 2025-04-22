from rest_framework import serializers

from pereval.models import Area, Image, Level, Pereval, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "patronymic", "phone"]
        extra_kwargs = {
            "email": {"validators": []},
        }

    def validate(self, data):
        if not data.get("email") or not data.get("first_name") or not data.get("last_name"):
            raise serializers.ValidationError("Поля email, first_name, last_name обязательны")
        return data

    def create(self, validated_data):
        email = validated_data.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            return user
        return User.objects.create(**validated_data)


class AreaSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(source="parent.id", required=False, allow_null=True)

    class Meta:
        model = Area
        fields = ["title", "parent_id"]

    def validate(self, data):
        if not data.get("title"):
            raise serializers.ValidationError("Поле title обязательно")
        return data


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ["winter", "summer", "autumn", "spring"]


class ImageDataSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False, allow_blank=True)


class CoordsSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    height = serializers.IntegerField()

    def validate(self, data):
        if not (-90 <= data["latitude"] <= 90):
            raise serializers.ValidationError("Широта должна быть в диапазоне от -90 до 90")
        if not (-180 <= data["longitude"] <= 180):
            raise serializers.ValidationError("Долгота должна быть в диапазоне от -180 до 180")
        if data["height"] < 0:
            raise serializers.ValidationError("Высота не может быть отрицательной")
        return data


class PerevalSerializer(serializers.Serializer):
    beauty_title = serializers.CharField(max_length=50, required=False, allow_null=True)
    title = serializers.CharField(max_length=255)
    other_titles = serializers.CharField(max_length=255, required=False, allow_null=True)
    connect = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    coords = CoordsSerializer()
    level = LevelSerializer()
    images = ImageDataSerializer(many=True, required=False)

    def validate(self, data):
        if not data["title"].strip():
            raise serializers.ValidationError("Название перевала не может быть пустым")
        return data


class SubmitDataSerializer(serializers.Serializer):
    user = UserSerializer()
    area = AreaSerializer()
    pereval = PerevalSerializer()


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ["title", "image", "date_added"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class PerevalDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    area = AreaSerializer()
    coords = CoordsSerializer(source="*")
    level = LevelSerializer()
    images = ImageSerializer(many=True)
    status = serializers.CharField()

    class Meta:
        model = Pereval
        fields = [
            "id",
            "beauty_title",
            "title",
            "other_titles",
            "connect",
            "user",
            "area",
            "coords",
            "level",
            "images",
            "status",
            "date_added",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["coords"] = {
            "latitude": data["coords"]["latitude"],
            "longitude": data["coords"]["longitude"],
            "height": data["coords"]["height"],
        }
        return data

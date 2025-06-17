from rest_framework import serializers

from models_app.models import Access

class AccessListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    user = serializers.SerializerMethodField()
    role = serializers.CharField(required=True)

    def get_user(self, obj: Access) -> dict[str, str]:
        return {
            'id': obj.user.id,
            'username': obj.user.username,
        }

from rest_framework import serializers


class AccessListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    user = serializers.SerializerMethodField()
    role = serializers.CharField(required=True)

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
        }

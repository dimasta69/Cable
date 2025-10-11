from rest_framework import serializers


class AccessSerializers(serializers.Serializer):
    id = serializers.IntegerField()
    role = serializers.CharField()
    object_id = serializers.IntegerField()
    object_type = serializers.CharField(source='object_type.model')


class UsersListSerializers(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    access = serializers.SerializerMethodField()

    def get_access(self, obj):
        if obj.access.exists():
            return AccessSerializers(obj.access.all(), many=True).data
        return []

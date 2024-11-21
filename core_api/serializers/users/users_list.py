from rest_framework import serializers


class UsersListSerializers(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()

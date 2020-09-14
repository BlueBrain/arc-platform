from rest_framework import serializers

from arcv2_platform.matchmaking.models import Request, Supply


class RequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Request

        fields = '__all__'
        read_only_fields = ('id', 'creator', 'creation_time', 'updater', 'update_time')


class SupplySerializer(serializers.ModelSerializer):

    class Meta:
        model = Supply

        fields = '__all__'
        read_only_fields = ('id', 'creator', 'creation_time', 'updater', 'update_time')

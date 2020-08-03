from django.db import models
from django.contrib.auth.models import User

from rest_framework import serializers

from jsonfield import JSONField

from .models import Hospital
from .models import Region


class UserSerializer(serializers.ModelSerializer):
    token = serializers.CharField(label='Token')
    role = serializers.CharField(label='Role')

    class Meta:
        model = User
        fields = ('username', 'role', 'token')


class HealthStatsSerializerModel(models.Model):
    total = models.PositiveIntegerField('Total')
    ageGroup = JSONField('Age Group')
    gender = JSONField('Gender')

    class Meta:
        managed = False


class HealthStatsSerializer(serializers.ModelSerializer):
    diseases_details = serializers.JSONField()

    class Meta:
        model = HealthStatsSerializerModel
        fields = ('total', 'ageGroup', 'gender', 'diseases_details')


class DetailedHealthStatsModel(models.Model):
    name = models.CharField('Name', max_length=31)

    class Meta:
        managed = False


class DetailedHealthStatsSerializer(serializers.ModelSerializer):
    values = serializers.JSONField()

    class Meta:
        model = DetailedHealthStatsModel
        fields = ('name', 'values')


class TimeseriesHealthStatsModel(models.Model):
    date = models.CharField('Date', max_length=10)

    class Meta:
        managed = False


class TimeseriesHealthStatsSerializer(serializers.ModelSerializer):
    values = serializers.JSONField()

    class Meta:
        model = TimeseriesHealthStatsModel
        fields = ('date', 'values')


class HospitalSerializer(serializers.ModelSerializer):
    region = serializers.CharField(source='region.name')
    province = serializers.CharField(source='province.name')

    class Meta:
        model = Hospital
        exclude = ('id', 'in_master_list', 'created_at', 'modified_at', 'logo', 'type')


class RegionSerializer(serializers.ModelSerializer):
    provinces = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
     )

    class Meta:
        model = Region
        fields = ('name', 'lng', 'lat', 'zoom', 'color', 'rgb', 'provinces')
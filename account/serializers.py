from django.contrib.auth.models import Group, User
from rest_framework import serializers

from membership.utils import check_membership

from .models import Profile
from . import user

class CommitteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name',)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('liu_card_id',)


class UserSerializer(serializers.ModelSerializer):
    committees = serializers.SerializerMethodField()
    membership = serializers.SerializerMethodField()
    pretty_name = serializers.SerializerMethodField()
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'pretty_name', 'committees', 'membership', 'profile',)

    def get_membership(self, obj):
        return check_membership(obj.username)
    
    def get_pretty_name(self, obj):
        return obj.get_full_name() if obj.get_full_name() else obj.get_username()

    def get_committees(self, obj):
        # TODO: fix this
        committees = Group.objects.filter(id__in=obj.groups.all())
        return CommitteeSerializer(committees, many=True).data

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        # Unless the application properly enforces that this field is
        # always set, the follow could raise a `DoesNotExist`, which
        # would need to be handled.
        profile = ""
        if hasattr(instance, 'profile'):
            profile = instance.profile 
        else:
            profile = Profile()

        # instance.username = validated_data.get('username', instance.username) # Username should never be updated
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        profile.liu_card_id = profile_data.get(
            'liu_card_id',
            profile.liu_card_id
        )

        profile.save()

        return instance

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        Profile.objects.create(user=user, **profile_data)
        return user


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')
        read_only_fields = ('id', 'username', 'first_name', 'last_name')


from django.contrib.auth.models import Group, User
from rest_framework import serializers

from account.models import Profile
from voting.models import Section

import account.user as user


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'name',)


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
    sections = serializers.SerializerMethodField()
    admin_sections = serializers.SerializerMethodField()
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'committees', 'sections', 'admin_sections', 'profile',)

    def get_sections(self, obj):
        sections = Section.objects.filter(user_group_id__in=obj.groups.all())
        return SectionSerializer(sections, many=True).data

    def get_admin_sections(self, obj):
        sections = Section.objects.filter(admin_group_id__in=obj.groups.all())
        return SectionSerializer(sections, many=True).data

    def get_committees(self, obj):
        committees = Group.objects.filter(id__in=obj.groups.all(), section_user_group=None, section_admin_group=None)
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

        # add user to section groups
        user.add_to_section_groups(instance)

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


class DetailedSectionSerializer(serializers.ModelSerializer):
    administrators = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ('id', 'name', 'administrators')

    def get_administrators(self, obj):
        admins = User.objects.filter(groups__name=obj.admin_group.name)
        return SimpleUserSerializer(admins, many=True).data

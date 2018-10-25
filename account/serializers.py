from django.contrib.auth.models import Group, User, Profile
from rest_framework import serializers

from voting.models import Section


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'name',)


class CommitteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name',)


class ProfileSerialize(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('liu-card-id',)


class UserSerializer(serializers.ModelSerializer):
    committees = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'committees', 'sections', 'profile',)

    def get_sections(self, obj):
        sections = Section.objects.filter(admin_group_id__in=obj.groups.all())
        return SectionSerializer(sections, many=True).data

    def get_committees(self, obj):
        committees = Group.objects.filter(id__in=obj.groups.all(), section_user_group=None, section_admin_group=None)
        return CommitteeSerializer(committees, many=True).data


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class DetailedSectionSerializer(serializers.ModelSerializer):
    administrators = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ('id', 'name', 'administrators')

    def get_administrators(self, obj):
        admins = User.objects.filter(groups__name=obj.admin_group.name)
        return SimpleUserSerializer(admins, many=True).data

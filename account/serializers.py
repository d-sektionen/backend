from django.contrib.auth.models import Group, User
from rest_framework import serializers

from voting.models import Section


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'name',)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    sections = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'groups', 'sections')

    def get_sections(self, obj):
        sections = Section.objects.filter(admin_group_id__in=obj.groups.all())
        return SectionSerializer(sections, many=True).data


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
